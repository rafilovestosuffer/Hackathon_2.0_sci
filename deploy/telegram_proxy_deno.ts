// Deno Deploy: transparent proxy to api.telegram.org.
// HF Spaces free egress blocks Telegram directly; the Space calls this proxy
// instead (set TELEGRAM_API_BASE=https://<project>.deno.dev on the Space).
// Forwards every path/method/body unchanged, incl. /bot<token>/... and
// /file/bot<token>/... — so both sendMessage and file downloads work.
Deno.serve(async (req: Request) => {
  const url = new URL(req.url);
  const target = "https://api.telegram.org" + url.pathname + url.search;
  return await fetch(target, {
    method: req.method,
    headers: req.headers,
    body: (req.method === "GET" || req.method === "HEAD") ? undefined : req.body,
  });
});
