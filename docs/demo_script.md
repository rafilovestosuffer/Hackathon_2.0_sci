# SkinAI Bangladesh — Demo Video Script
# Target duration: 4 minutes (±30 seconds)
# Format: Screen recording + voice-over narration
# Tool: OBS Studio (recommended) or Loom
# Resolution: 1920×1080, HF Space loaded in Chrome, full width, sidebar visible

---

## PRE-RECORDING CHECKLIST

- [ ] HF Space loaded and warm: https://huggingface.co/spaces/rafilovestosuffer/skinai-bangladesh
- [ ] Chrome window: 1280px wide minimum, sidebar pinned open
- [ ] Microphone tested — clear, no background noise
- [ ] Test image ready: `docs/test_scabies.jpg` (or any clear skin photo for the real model demo)
- [ ] Bengali voice file ready: `docs/demo_voice.wav` (see recording text below)
- [ ] OBS scene: Desktop capture, crop to browser window
- [ ] Run demo button once before recording to warm up session state

---

## SEGMENT 0 — Title Slide (0:00–0:15)

> **[No screen action — static title card or black screen with text overlay]**

**Narration (read aloud):**

> "Bangladesh has approximately one dermatologist for every two hundred and fifty thousand people.
> In rural areas, eighty percent of skin conditions go untreated — or are mistreated by unlicensed practitioners.
> This is SkinAI Bangladesh."

**On-screen text (optional overlay):**
```
SkinAI Bangladesh
সঠিক রোগী → সঠিক ডাক্তার → সঠিক সময়
Right patient → Right doctor → Right time
SciBlitz AI Challenge 2026 — IEEE SB CUET
```

---

## SEGMENT 1 — Rahim's Story (0:15–0:45)

> **[Screen: HF Space homepage — sidebar visible, Tab 1 open, nothing filled yet]**

**Narration (read aloud):**

> "Meet Rahim. He is a farmer in Rangpur. He has noticed a spreading rash on his arms and stomach for ten days.
> The nearest dermatologist is four hours away by bus — and costs fifteen hundred taka he cannot spare.
> He opens SkinAI Bangladesh on his phone.
> He speaks in Bengali. He takes a photo.
> In seconds, he has a diagnosis, a severity score, and a referral letter — in his own language."

> **[Pause 1 second — let the page breathe before moving on]**

---

## SEGMENT 2 — Bengali Voice Input (0:45–1:20)

> **[Screen: Tab 1, left column — mic input visible]**

**Narration:**
> "Rahim describes his symptoms in Bengali using the built-in microphone."

> **[Action: Click mic icon, wait for recording indicator, then speak the following sentence clearly:]**

**Bengali sentence to speak during recording:**

> **"আমার সারা শরীলে চুলকানি হচ্ছে। দশ দিন ধরে ছড়িয়ে পড়ছে। জ্বরও আছে এবং ব্যথা হচ্ছে।"**

*(Translation: "I have itching all over my body. It has been spreading for ten days. I also have fever and pain.")*

> **[Action: Click stop. Wait for transcription spinner to finish (~3–5 seconds).]**

> **[Screen: Transcript appears, then patient history table populates below]**

**Narration:**
> "faster-whisper transcribes the Bengali audio offline — no internet needed for speech recognition.
> Gemini extracts nine structured fields: chief complaint, symptoms, affected area, duration, and more.
> All of this appears automatically in the patient history table."

> **[Gesture toward the populated table with the cursor]**

---

## SEGMENT 3 — Image Upload → Classification → GradCAM (1:20–2:10)

> **[Screen: Tab 1, right column — image uploader visible]**

**Narration:**
> "Now Rahim uploads a photo of the affected area."

> **[Action: Drag test image into the upload dropzone. Wait for the analysis spinner (~2–3 seconds).]**

> **[Screen: Disease card appears — disease name in English and Bengali, confidence bar, caption pill]**

**Narration:**
> "BD-SkinNet — a Swin Transformer with CBAM attention, trained on data from Faridpur and Rangpur Medical College Hospitals — identifies the disease.
> The confidence caption tells Rahim in Bengali whether the model is certain or whether he should see a doctor regardless."

> **[Gesture to the confidence caption pill]**

> **[Screen: Scroll down slightly to show GradCAM heatmap overlay]**

**Narration:**
> "GradCAM-plus-plus generates a heatmap showing exactly which pixels the model used to reach its decision.
> The coverage percentage — how much of the skin is affected — feeds directly into the triage engine."

---

## SEGMENT 4 — Severity Tier + Bengali Triage Badge (2:10–2:35)

> **[Screen: Triage badge visible — colour, tier number, Bengali action text]**

**Narration:**
> "The four-signal triage engine combines the disease class, model confidence, GradCAM coverage, and any escalation keywords from the voice recording — like fever or spreading.
> It outputs a colour-coded urgency badge in Bengali and English.
> No disease class maps to Tier 3 directly — Tier 3 is only reached through escalation.
> This is medically safer than a simple lookup."

> **[Point to the Bengali action text in the badge]**

**Narration:**
> "The badge tells Rahim in his own language exactly what to do and where to go."

---

## SEGMENT 5 — Hospital Map via Demo Mode (2:35–3:00)

> **[Action: Click "Load Demo (Scabies — Tier 3)" in the sidebar. Wait for rerun (~1 second).]**

> **[Screen: All tabs populated. Scroll to hospital section in Tab 1.]**

**Narration:**
> "For Tier 3 cases — emergency — the app queries the Overpass API to find the five nearest hospitals using OpenStreetMap data.
> No API key is required."

> **[Action: Type "Rangpur" in the district input box. Wait for hospital spinner (~3–5 seconds).]**

> **[Screen: Hospital table with names and distances, Folium map with pins]**

**Narration:**
> "The top hospital is automatically injected into the referral letter.
> Rahim can tap the map pin, get directions, and go."

---

## SEGMENT 6 — PDF Referral Letter (3:00–3:25)

> **[Action: Click Tab 3 "রেফারেল পত্র". Show the summary metrics cards.]**

**Narration:**
> "Tab 3 generates a four-section referral letter with one click."

> **[Action: Click "Generate Referral Letter" button. Wait for spinner (~2–3 seconds).]**

> **[Screen: "✅ Referral letter generated!" success message. Download button appears.]**

> **[Action: Click download. PDF opens (or show a pre-rendered preview if screen recording allows).]**

**Narration:**
> "Section 1 — patient history from the voice recording.
> Section 2 — the GradCAM heatmap with coverage percentage.
> Section 3 — the AI diagnosis with confidence and differential.
> Section 4 — the triage recommendation, the hospital name and address, and the full instructions in Bengali.
> Everything Rahim needs to hand to the doctor. Zero manual input required."

---

## SEGMENT 7 — RAG Chatbot (3:25–3:50)

> **[Action: Click Tab 2 "প্রশ্ন করুন". Show the disease context banner at the top.]**

**Narration:**
> "The RAG chatbot answers medical questions in Bengali or English — grounded in CDC, NIH, WHO, and DGHS Bangladesh guidelines.
> It knows the current diagnosis and answers in that context."

> **[Action: Type in the chat input:]**

**Question to type:**
> `স্ক্যাবিসের লক্ষণ কী এবং এটি কি ছোঁয়াচে?`

*(Translation: "What are the symptoms of scabies and is it contagious?")*

> **[Wait for RAG spinner (~3–5 seconds). Screen: Answer appears in green box with source tags (CDC/NIH/WHO/DGHS).]**

**Narration:**
> "The answer is grounded — every response cites only authoritative public-health sources.
> No medication names. No prescriptions. Triage and referral only — as required."

---

## SEGMENT 8 — Impact Slide + Close (3:50–4:00)

> **[Screen: Switch to title card / black screen with text overlay — same as Segment 0]**

**Narration:**

> "Rahim now has a plan. He knows his diagnosis. He knows his urgency level.
> He has a referral letter for Rangpur Medical College Hospital.
> He does not need to go to Dhaka.
> Right patient. Right doctor. Right time.
> SkinAI Bangladesh — SciBlitz AI Challenge 2026."

**On-screen text:**
```
164 tests passing
F1: 92.46% | AUC-ROC: 0.9937
7 disease classes · Bengali voice · GradCAM++ · RAG · PDF
Live: huggingface.co/spaces/rafilovestosuffer/skinai-bangladesh
```

---

## RECORDING NOTES

- Keep cursor movements slow and deliberate — judges are watching
- Pause 0.5–1 second after each major UI element appears before narrating it
- If a spinner takes longer than expected, keep narrating — don't go silent
- The demo mode button guarantees Tier 3 with hospital map regardless of model output — use it for segments 5–8 if the real model doesn't produce Tier 3
- Record the Bengali voice sentence (Segment 2) separately first and play it back to check clarity before the main recording
- Total target: 4 minutes. If under 3:30, slow down transitions. If over 4:30, cut the RAG segment to one exchange only.

---

## POST-RECORDING

- [ ] Upload to YouTube (unlisted) or Google Drive (link sharing: anyone with link)
- [ ] Add link to README.md under "🎬 Demo Video:" line
- [ ] Test link from incognito browser before submitting
