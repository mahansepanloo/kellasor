FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:0.9.8 /uv /uvx /bin/

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
    libpq-dev \
    build-essential \
    git \
    gh \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml uv.lock ./

RUN uv sync --no-install-project --frozen -n

RUN mkdir -p /app/logs/

FROM python:3.12-slim AS app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH="/app/.venv/bin:$PATH"
ENV VIRTUAL_ENV="/app/.venv"

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
    libpq-dev \
    supervisor \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=builder /app /app

COPY . .
