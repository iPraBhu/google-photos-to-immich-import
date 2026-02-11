# syntax=docker/dockerfile:1.4
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    ca-certificates \
    jq \
    exiftool \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY ./app/requirements.txt ./requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Playwright dependencies (optional)
ARG ENABLE_PLAYWRIGHT=0
RUN if [ "$ENABLE_PLAYWRIGHT" = "1" ]; then \
    pip install playwright && \
    playwright install --with-deps chromium; \
    fi

# --- Web image ---
FROM base AS web
COPY ./app /app
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# --- Worker image ---
FROM base AS worker
COPY ./app /app
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["rq", "worker", "-u", "redis://redis:6379/0", "import-queue"]
