// Cloudflare Worker: transparent proxy to api.telegram.org.
// HF Spaces free egress blocks Telegram directly; the Space calls this Worker
// instead (set TELEGRAM_API_BASE=https://<name>.<subdomain>.workers.dev).
// Forwards every path/method/body unchanged, incl. /bot<token>/... and
// /file/bot<token>/... — so both sendMessage and file downloads work.
export default {
  async fetch(request) {
    const url = new URL(request.url);
    const target = "https://api.telegram.org" + url.pathname + url.search;
    const init = {
      method: request.method,
      headers: request.headers,
      body: (request.method === "GET" || request.method === "HEAD")
        ? undefined
        : request.body,
    };
    return fetch(target, init);
  },
};
