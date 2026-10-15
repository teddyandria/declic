# Image de l'API Déclic (FastAPI). Construite par docker compose ou par l'hébergeur.
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.11 /uv /bin/uv

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

# Dépendances d'abord : cette couche reste en cache tant que uv.lock ne change pas.
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --locked --no-dev --no-install-project

COPY app ./app
COPY alembic.ini ./
COPY migrations ./migrations

RUN useradd --create-home --uid 1000 declic
USER declic

EXPOSE 8000
# Au démarrage : migrations, puis l'API. PORT est fourni par certains hébergeurs (Railway…) ; 8000 sinon.
# HOST : 0.0.0.0 (IPv4) par défaut ; « :: » sur Railway, dont le réseau privé passe par IPv6.
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn app.main:app --host ${HOST:-0.0.0.0} --port ${PORT:-8000} --proxy-headers --forwarded-allow-ips='*'"]
