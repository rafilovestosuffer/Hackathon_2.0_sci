"""
whatsapp/ — Zero-cost WhatsApp + Telegram bot integration for SkinAI Bangladesh.

Public modules:
  replies       — Bengali + English message templates
  state         — Per-phone state machine with TTL eviction + dedupe
  meta_client   — Meta WhatsApp Cloud API HTTP wrapper
  telegram_client — Telegram Bot API HTTP wrapper
  router        — Maps incoming message + state → handler → outgoing reply
"""
