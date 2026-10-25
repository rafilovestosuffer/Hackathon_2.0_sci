/* SkinAI Lite — offline-first store-and-forward triage.
 *
 * 1. Photo + warning-sign checklist are captured with no network.
 * 2. Any warning sign → "go to a health facility today" is shown at once, offline.
 * 3. The photo is shrunk on the phone (≤640 px JPEG) and queued in IndexedDB.
 * 4. When the phone is online, queued cases are sent to /api/cases, which runs
 *    BD-SkinNet + the triage engine; the result comes back to this page.
 * 5. If the patient consented, a doctor can review it; the decision appears here.
 *
 * Rule: urgency shown = the stricter of the offline warning-sign advice and the
 * server tier. A doctor's decision, once given, is shown as the final word.
 */
"use strict";

const API = "/api/cases";
const MAX_SIDE = 640;
const JPEG_QUALITY = 0.7;
const FLAG_BN = { fever: "জ্বর", spreading: "দ্রুত ছড়াচ্ছে", pain: "তীব্র ব্যথা", bleeding: "রক্তপাত" };
const TIER_BN = {
  0: "সুস্থ · Healthy",
  1: "জরুরি নয় · Non-urgent",
  2: "নিয়মিত · Routine (48 ঘণ্টার মধ্যে)",
  3: "জরুরি · Urgent — আজই",
};

/* ---------- IndexedDB (tiny wrapper) ---------- */
const DB_NAME = "skinai-lite";
const STORE = "cases";

function openDb() {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, 1);
    req.onupgradeneeded = () => req.result.createObjectStore(STORE, { keyPath: "localId" });
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

async function tx(mode, fn) {
  const db = await openDb();
  return new Promise((resolve, reject) => {
    const t = db.transaction(STORE, mode);
    const out = fn(t.objectStore(STORE));
    t.oncomplete = () => resolve(out && out.result !== undefined ? out.result : out);
    t.onerror = () => reject(t.error);
  });
}

const putCase = (c) => tx("readwrite", (s) => s.put(c));
const allCases = () => tx("readonly", (s) => s.getAll());

/* ---------- Image shrink ---------- */
function shrink(file) {
  return new Promise((resolve, reject) => {
    const url = URL.createObjectURL(file);
    const img = new Image();
    img.onload = () => {
      const scale = Math.min(1, MAX_SIDE / Math.max(img.width, img.height));
      const w = Math.round(img.width * scale);
      const h = Math.round(img.height * scale);
      const canvas = document.createElement("canvas");
      canvas.width = w;
      canvas.height = h;
      canvas.getContext("2d").drawImage(img, 0, 0, w, h);
      URL.revokeObjectURL(url);
      canvas.toBlob((b) => (b ? resolve(b) : reject(new Error("encode failed"))), "image/jpeg", JPEG_QUALITY);
    };
    img.onerror = () => { URL.revokeObjectURL(url); reject(new Error("not an image")); };
    img.src = url;
  });
}

/* ---------- UI helpers ---------- */
const $ = (id) => document.getElementById(id);
const show = (id) => ["home", "form", "saved"].forEach((s) => $(s).classList.toggle("hidden", s !== id));
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

function setNet() {
  const on = navigator.onLine;
  $("net").textContent = on ? "অনলাইন · Online" : "অফলাইন · Offline";
  $("net").className = "pill " + (on ? "on" : "off");
}

function redFlagAlert(flags) {
  if (flags.length) {
    return `<div class="alert red"><strong>⚠ আজই নিকটস্থ স্বাস্থ্যকেন্দ্রে যান</strong>
      Go to the nearest health facility today.<br>
      <span>সতর্ক লক্ষণ: ${flags.map((f) => esc(FLAG_BN[f])).join(", ")}</span></div>`;
  }
  return `<div class="alert grey"><strong>✓ সংরক্ষণ হয়েছে · Saved</strong>
    ইন্টারনেট পেলে নিজে থেকেই পরীক্ষা হবে। অবস্থা খারাপ হলে অপেক্ষা না করে স্বাস্থ্যকেন্দ্রে যান।<br>
    <span class="muted">Will be checked automatically when online. If it gets worse, don't wait — go to a health facility.</span></div>`;
}

function shownTier(c) {
  const offline = c.flags.length ? 3 : 0;
  const server = c.result ? c.result.tier : 0;
  return Math.max(offline, server);
}

function statusLine(c) {
  switch (c.state) {
    case "queued": return "⏳ পাঠানোর অপেক্ষায় · Waiting to send";
    case "retry": return "⏳ মডেল এখন চালু নেই — আবার চেষ্টা হবে · Model busy, will retry";
    case "blurry": return "📷 ছবি অস্পষ্ট — নতুন ছবি দিন · Photo too blurry, please take a new case";
    case "error": return "⚠ পাঠানো যায়নি · Could not send: " + esc(c.error || "");
    case "done": return c.caseId ? (c.doctor ? "👩‍⚕️ ডাক্তার দেখেছেন · Doctor reviewed" : "✓ ফলাফল এসেছে; ডাক্তারের অপেক্ষায় · Result in; waiting for doctor")
                                  : "✓ ফলাফল এসেছে · Result in";
    default: return "";
  }
}

async function render() {
  const cases = (await allCases()).sort((a, b) => b.createdAt - a.createdAt);
  const q = $("queue");
  if (!cases.length) {
    q.innerHTML = `<p class="muted">এখনো কোনো কেস নেই · No cases yet.</p>`;
    return;
  }
  q.innerHTML = cases.map((c) => {
    const t = shownTier(c);
    const thumb = c.thumbUrl ? `<img src="${c.thumbUrl}" alt="Skin photo">` : "";
    let body = "";
    if (c.flags.length) body += `<div class="alert red" style="margin:8px 0;padding:8px 10px;"><strong>⚠ আজই যান · Go today</strong></div>`;
    if (c.result) {
      const r = c.result;
      body += `<div><strong>${esc(r.disease_bn)}</strong> (${esc(r.disease.replace(/_/g, " "))}) — ${Math.round(r.confidence * 100)}%</div>
        <div>${esc(TIER_BN[t])}</div>
        <div class="muted">${esc(t === r.tier ? r.action_bn : "সতর্ক লক্ষণ থাকায় আজই যান · Go today because of warning signs")}</div>
        <ul>${(r.reasons || []).map((x) => `<li>${esc(x.bn)}</li>`).join("")}</ul>`;
    }
    if (c.doctor) {
      const d = c.doctor;
      body += `<div class="doc">👩‍⚕️ ডাক্তারের মতামত · Doctor: ${esc(d.dr_disease.replace(/_/g, " "))} — ${esc(TIER_BN[d.dr_tier])}<br>
        ${esc(d.dr_action_bn)}${d.dr_note ? "<br>📝 " + esc(d.dr_note) : ""}</div>`;
    }
    const when = new Date(c.createdAt).toLocaleString();
    return `<div class="card case t${c.doctor ? c.doctor.dr_tier : t}">${thumb}
      <div class="muted">${esc(when)} · ${Math.round(c.bytes / 1024)} KB</div>
      <div>${statusLine(c)}</div>${body}<div style="clear:both"></div></div>`;
  }).join("");
}

/* ---------- Sync ---------- */
let syncing = false;

async function syncOne(c) {
  const fd = new FormData();
  fd.append("image", c.blob, "lesion.jpg");
  c.flags.forEach((f) => fd.append("red_flags", f));
  fd.append("district", c.district || "");
  fd.append("consent", c.consent ? "true" : "false");
  fd.append("client_ts", new Date(c.createdAt).toISOString());
  const res = await fetch(API, { method: "POST", body: fd });
  const data = await res.json().catch(() => ({}));
  if (res.ok) {
    c.state = "done";
    c.result = data;
    c.caseId = data.case_id || null;
  } else if (res.status === 503 || res.status === 429) {
    c.state = "retry";
  } else if (res.status === 422) {
    c.state = "blurry";
  } else {
    c.state = "error";
    c.error = data.error || String(res.status);
  }
  await putCase(c);
}

async function pollDoctor(c) {
  const res = await fetch(`${API}/${encodeURIComponent(c.caseId)}`);
  if (!res.ok) return;
  const data = await res.json();
  if (data.status && data.status !== "pending") {
    c.doctor = data;
    await putCase(c);
  }
}

async function syncAll() {
  if (syncing || !navigator.onLine) return;
  syncing = true;
  try {
    for (const c of await allCases()) {
      try {
        if (c.state === "queued" || c.state === "retry") await syncOne(c);
        else if (c.state === "done" && c.caseId && !c.doctor) await pollDoctor(c);
      } catch (e) {
        // network dropped mid-sync — leave the case queued for next time
      }
    }
  } finally {
    syncing = false;
    render();
  }
}

/* ---------- Form ---------- */
let pending = null; // { blob, thumbUrl }

$("photo").addEventListener("change", async (e) => {
  const file = e.target.files && e.target.files[0];
  if (!file) return;
  try {
    const blob = await shrink(file);
    const thumbUrl = await new Promise((r) => { const fr = new FileReader(); fr.onload = () => r(fr.result); fr.readAsDataURL(blob); });
    pending = { blob, thumbUrl };
    $("preview").src = thumbUrl;
    $("preview").style.display = "block";
    $("size").textContent = `পাঠানোর আকার · Upload size: ${Math.round(blob.size / 1024)} KB (মূল · original ${Math.round(file.size / 1024)} KB)`;
    $("save").disabled = false;
  } catch (err) {
    $("size").textContent = "ছবিটি পড়া যায়নি · Could not read this image.";
    $("save").disabled = true;
  }
});

function resetForm() {
  pending = null;
  $("photo").value = "";
  $("preview").style.display = "none";
  $("size").textContent = "";
  document.querySelectorAll('input[name="flag"]').forEach((i) => (i.checked = false));
  $("district").value = "";
  $("consent").checked = false;
  $("save").disabled = true;
}

$("newCase").addEventListener("click", () => { resetForm(); show("form"); });
$("cancel").addEventListener("click", () => show("home"));
$("backHome").addEventListener("click", () => { show("home"); render(); });
$("syncNow").addEventListener("click", syncAll);

$("save").addEventListener("click", async () => {
  if (!pending) return;
  const flags = [...document.querySelectorAll('input[name="flag"]:checked')].map((i) => i.value);
  const c = {
    localId: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    createdAt: Date.now(),
    blob: pending.blob,
    bytes: pending.blob.size,
    thumbUrl: pending.thumbUrl,
    flags,
    district: $("district").value.trim(),
    consent: $("consent").checked,
    state: "queued",
  };
  await putCase(c);
  $("savedAlert").innerHTML = redFlagAlert(flags);
  show("saved");
  syncAll();
});

/* ---------- Boot ---------- */
window.addEventListener("online", () => { setNet(); syncAll(); });
window.addEventListener("offline", setNet);
setNet();
render();
syncAll();
setInterval(syncAll, 60000);

if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("sw.js", { scope: "./" }).catch(() => {});
}
