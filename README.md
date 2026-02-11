# Google Photos to Immich Importer

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)

A robust, enterprise-grade, FOSS tool to import Google Photos public shared album links into [Immich](https://github.com/immich-app/immich), recreating albums and uploading all media with full metadata preservation. Built for reliability, security, and extensibility.


## Features


## Quick Start

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
- At least 4GB RAM available for Docker

### Setup (Windows)
```cmd
# Run the setup script (it will build and start everything automatically)
setup.bat
```

### Setup (Linux/Mac)
```bash
# Run the setup script (it will build and start everything automatically)
./setup.sh
```

### Manual Setup
If you prefer to run commands manually:
```bash
# Clone the repository
git clone https://github.com/iPraBhu/google-photos-to-immich-import.git
cd google-photos-to-immich-import

# Start all services (database migrations run automatically)
docker compose up -d --build
```

### Access the Application
- **Web UI**: http://localhost:8000
- **Immich** (if running): http://localhost:2283

### View Logs
```bash
docker compose logs -f
```

### Stop Services
```bash
docker compose down
```


## Environment Variables

| Variable           | Description                                                                 | Example/Default Value                                      |
|--------------------|-----------------------------------------------------------------------------|------------------------------------------------------------|
| DATABASE_URL       | Postgres connection string                                                  | postgresql+psycopg2://gp_import:gp_import_pw@db:5432/google_photos_import |
| REDIS_URL          | Redis connection string                                                     | redis://redis:6379/0                                       |
| APP_SECRET_KEY     | Secret key for Fernet encryption of Immich credentials and API keys         | changeme (change this in production!)                      |
| ENABLE_PLAYWRIGHT  | Enable Playwright fallback for Google Photos extraction (0=off, 1=on)       | 0                                                          |
| LOG_LEVEL          | Log level for backend and worker                                            | info                                                       |

### .env Variable Details

**DATABASE_URL**

This variable specifies the connection string for the Postgres database. The format is:

   postgresql+psycopg2://<username>:<password>@<host>:<port>/<database>

In Docker Compose, the hostname `db` refers to the Postgres container defined in `docker-compose.yml`. This is not a typical localhost address, but a Docker network alias, allowing containers to communicate. The URL uses the `psycopg2` driver for SQLAlchemy compatibility.

Example:

   DATABASE_URL=postgresql+psycopg2://gp_import:gp_import_pw@db:5432/google_photos_import

If running locally (not in Docker), change `db` to `localhost` and ensure Postgres is running:

   DATABASE_URL=postgresql+psycopg2://gp_import:gp_import_pw@localhost:5432/google_photos_import

**REDIS_URL**

Specifies the Redis connection string. In Docker, `redis` is the hostname for the Redis container. For local development, use `localhost`.

**APP_SECRET_KEY**

Used for Fernet encryption of sensitive Immich credentials and API keys. Change this to a strong, random value in production.

**ENABLE_PLAYWRIGHT**

Set to `1` to enable headless browser extraction for Google Photos links if HTML parsing fails. Requires Playwright dependencies.

**LOG_LEVEL**

Controls log verbosity. Typical values: `info`, `debug`, `warning`, `error`.


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


## Immich API Key Instructions

## Immich Credentials Login


## Google Photos Public Links


## Data Volumes


## Alembic Migrations


## Tests


## Security


## Known Limitations


## Contributing
Pull requests, issues, and feature suggestions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License
MIT
