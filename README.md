# tinkerhub-auto-doc

Auto-detects daily event (Tue/Wed/Thu + any day), catches livestream, transcribes + visions, documents.

**Deploy:** `pip install -r requirements.txt && cp .env.example .env` (fill keys) then `python src/scheduler.py` or systemd/cron. Runs daily 18:00 IST. 3x/week = stays in free tier.

**Hybrid 1.5hr handling:** Groq Whisper -> timestamps -> ffmpeg frames (5/batch) -> Groq qwen3 vision -> Gemini flash summary -> `docs/YYYY-MM-DD.md`

**Placeholders:** `EVENT_CHECK_URL` / `LIVE_STREAM_URL` capture via yt-dlp - to be wired once logic repo is shared. No logic repo touched now.

`.env` gitignored. Keys are env vars only.
