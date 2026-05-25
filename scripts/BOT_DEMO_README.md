# Telegram Bot — Demo Day Quick Start

## Tomorrow, when you want to record the demo video

Open PowerShell:

```powershell
cd C:\Users\Rafi\Desktop\skinai-bangladesh
powershell -ExecutionPolicy Bypass -File scripts\start_bot.ps1
```

You will see this within ~30 seconds:

```
==============================================
 BOT IS LIVE
==============================================
  Open Telegram and message:  @SkinAIBDBot
  Tunnel URL: https://<random>-<words>.trycloudflare.com
==============================================
```

Then open Telegram, message `@SkinAIBDBot`, and the bot will reply.

## When you finish recording

Press **Ctrl+C** in the same PowerShell window. The script will:
- Unregister the Telegram webhook (so Telegram stops trying to deliver)
- Kill uvicorn and cloudflared
- Print "Stopped."

## What the script does

1. Reads `TELEGRAM_BOT_TOKEN` from `.env`
2. Starts uvicorn on `127.0.0.1:8765` (webhook server, FastAPI)
3. Starts a Cloudflare Tunnel pointing to it
4. Captures the random `https://*.trycloudflare.com` URL
5. Registers that URL with Telegram as the bot's webhook (retries 20× for DNS propagation)
6. Tails the uvicorn log so you can see incoming messages live

## Test conversation (verify before recording)

| You send | Bot replies |
|---|---|
| `/start` or `hi` | 👋 Bengali welcome + asks for district |
| `Rangpur` (or `ঢাকা`, `Dhaka`, etc.) | Acknowledges + asks for photo |
| any photo | Acknowledges + asks for voice or `skip` |
| `skip` | Triage result + PDF referral letter |
| any question | RAG knowledge-base answer (English/Bengali) |
| `নতুন` or `new` | Resets the conversation |

## If the bot does NOT reply

1. Look in the same PowerShell window — incoming `POST /webhook/telegram` lines should appear when you send a message. If they don't, Telegram isn't reaching the tunnel.
2. Check tunnel health from another terminal:
   ```powershell
   curl.exe https://<your-tunnel-url>/health
   ```
   Should return JSON. If 530 or HTML → tunnel died, restart the launcher.
3. Check Telegram's view of the webhook:
   ```powershell
   curl.exe https://api.telegram.org/bot$env:TELEGRAM_BOT_TOKEN/getWebhookInfo
   ```
   `last_error_message` will say what's broken.

## Important: the tunnel URL changes every run

Every time you run `start_bot.ps1` you get a NEW random URL. The script
re-registers the webhook automatically — you don't have to do anything.
But this means: do NOT save or share the URL. It's ephemeral.

## Logs (for debugging)

- `%TEMP%\skinai_bot\uvicorn.log` — every webhook request + response
- `%TEMP%\skinai_bot\cloudflared.log` — tunnel status

## Why we can't just use HF Space for the bot

HuggingFace Spaces blocks outbound HTTPS to `api.telegram.org` on free
tier (anti-spam policy). We verified this with a connectivity probe:
google.com, cloudflare.com, httpbin.org all respond — only Telegram
times out. The Streamlit UI on HF still works fine; only the bot needs
to run from your laptop.
