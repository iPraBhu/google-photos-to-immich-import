# Agents and Architecture

This project uses a modular, agent-based architecture to ensure robust, scalable, and maintainable imports from Google Photos to Immich.

## Main Agents

- **Web API (FastAPI):**
  - Handles all user requests, authentication, job creation, and status queries.
  - Provides REST endpoints and serves the frontend UI.

- **Worker (RQ):**
  - Executes long-running import jobs in the background.
  - Handles Google Photos album extraction, media download, deduplication, EXIF/XMP extraction, and upload to Immich.
  - Respects concurrency, resume, and cancellation.

- **Database (Postgres):**
  - Stores jobs, albums, items, progress, logs, and encrypted secrets.

- **Redis:**
  - Manages job queue and real-time event streaming.

## Security Agent
- All Immich secrets (API key or credentials) are encrypted at rest using Fernet and a server-side `APP_SECRET_KEY`.
- Secrets are never returned to the client after initial submission.

## Google Photos Extraction
- **HTML Parser Agent:** Attempts to extract album and media links from public Google Photos share pages using HTML parsing.
- **Playwright Agent (Optional):** If enabled, uses headless Chromium for fallback extraction when HTML parsing fails.

## Immich Integration
- **API Key Agent:** Uses Immich API key for authentication if provided.
- **Credentials Agent:** Logs in with Immich email/password to obtain a session token, which is stored encrypted and refreshed as needed.

## Logging
- Structured logs are written per job to `/data/logs/<job_id>.log` and recent lines are stored in the database for UI display.

## Concurrency and Resume
- Download and upload concurrency is configurable per job.
- Jobs are idempotent and can resume after interruption or worker restart.

## Extensibility
- The system is designed for easy extension with new agents (e.g., new import sources, additional metadata extraction, etc.).

---

For more details, see the main [README.md](README.md).
