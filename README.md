# Google Photos to Immich Importer

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)

A robust, enterprise-grade, FOSS tool to import Google Photos public shared album links into [Immich](https://github.com/immich-app/immich), recreating albums and uploading all media with full metadata preservation. Built for reliability, security, and extensibility.

---

## Features
- **Import Google Photos public album links** (no Google API/OAuth required)
- **Recreate albums and upload original media** to Immich
- **Preserve EXIF/XMP metadata** (no transcoding)
- **Immich API key or email/password login** (secure, encrypted at rest)
- **Resume, dedupe, and robust error handling**
- **Real-time progress UI** (single-page app)
- **Enterprise security:** secrets never leave the backend, encrypted at rest
- **Docker Compose deployment** for easy self-hosting

---

## Quick Start

### 1. Prerequisites
- Docker & Docker Compose
- Immich server (v1.100+ recommended)

### 2. Clone the Repository
```sh
git clone https://github.com/iPraBhu/google-photos-to-immich-import.git
cd google-photos-to-immich-import
```

### 3. Configure Environment
Copy the example environment file and edit as needed:
```sh
cp .env.example .env
# Edit .env to set APP_SECRET_KEY, etc.
```

### 4. Run with Docker Compose
```sh
docker compose up --build
```
- The web UI will be available at [http://localhost:8000](http://localhost:8000)
- Data and logs are stored in `./data/`

---

## Environment Variables

| Variable           | Description                                                                 | Example/Default Value                                      |
|--------------------|-----------------------------------------------------------------------------|------------------------------------------------------------|
| DATABASE_URL       | Postgres connection string                                                  | postgresql+psycopg2://gp_import:gp_import_pw@db:5432/google_photos_import |
| REDIS_URL          | Redis connection string                                                     | redis://redis:6379/0                                       |
| APP_SECRET_KEY     | Secret key for Fernet encryption of Immich credentials and API keys         | changeme (change this in production!)                      |
| ENABLE_PLAYWRIGHT  | Enable Playwright fallback for Google Photos extraction (0=off, 1=on)       | 0                                                          |
| LOG_LEVEL          | Log level for backend and worker                                            | info                                                       |

---

## Local Development (No Docker)

1. Install Python 3.11+, Node.js (if using Vite/React frontend), Postgres, and Redis.
2. Create and activate a virtualenv:
   ```sh
   python -m venv venv
   source venv/bin/activate
   pip install -r app/requirements.txt
   pip install -r app/requirements-dev.txt
   ```
3. Set up Postgres and Redis, and configure your `.env`.
4. Run Alembic migrations:
   ```sh
   alembic -c app/db/alembic.ini upgrade head
   ```
5. Start the backend:
   ```sh
   uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000
   ```
6. Start the worker:
   ```sh
   rq worker -u redis://localhost:6379/0 import-queue
   ```
7. (If using Vite/React) Start the frontend dev server in `frontend/`.

---

## Immich API Key Instructions
- In Immich, go to your user profile > API Keys > Create API Key
- Paste the key in the web UI (preferred if available)

## Immich Credentials Login
- Enter your Immich email and password in the web UI
- The system logs in and stores a session token (encrypted)
- No secrets are returned to the browser after submission
- If token expires, the worker will attempt to refresh/re-login

---

## Google Photos Public Links
- Only public shared album links (e.g., https://photos.app.goo.gl/...) are supported
- No official Google API is used; best-effort HTML parsing
- If Google changes the share page, import may break (see logs)

---

## Data Volumes
- `./data:/data` is used for staging downloads and logs
- `db_data` for Postgres

---

## Alembic Migrations
- Run migrations automatically on startup
- To create new migrations: `docker compose run web alembic revision --autogenerate -m "message"`

---

## Tests
- Run tests: `docker compose run web pytest`
- Includes tests for encryption, dedupe, parser, and Immich login client

---

## Security
- All Immich secrets (API key or credentials) are encrypted at rest using Fernet and a server-side `APP_SECRET_KEY`.
- Secrets are never returned to the client after initial submission.

---

## Known Limitations
- Google Photos public link parsing is best-effort and may break if Google changes their HTML
- Playwright fallback is optional (set `ENABLE_PLAYWRIGHT=1`)

---

## Contributing
Pull requests, issues, and feature suggestions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License
MIT
