# TrendRadar API — production image for Railway / Fly / any Docker host.
# Two-stage build keeps the runtime slim (no build tools, no wheels cache).
FROM python:3.11-slim AS builder

WORKDIR /build

# System deps for asyncpg (libpq) + bcrypt (libffi) wheel builds.
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
# Install into a throwaway prefix so we can COPY it into the final image.
RUN pip install --no-cache-dir --prefix=/install .


FROM python:3.11-slim

WORKDIR /app

# Only the runtime libs we need — libpq for asyncpg.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Bring over the installed packages from the builder stage.
COPY --from=builder /install /usr/local

# App source — .dockerignore filters out .venv, __pycache__, tests, etc.
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini .
COPY scripts ./scripts

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_ENV=production

# Railway/Fly inject PORT at runtime. Default to 8000 locally.
ENV PORT=8000
EXPOSE 8000

# Run migrations then start the server. Single instance for MVP (no worker pool).
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1 --proxy-headers --forwarded-allow-ips='*'"]
