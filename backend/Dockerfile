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

RUN useradd --create-home --uid 1000 declic
USER declic

EXPOSE 8000
# PORT est fourni par certains hébergeurs (Railway…) ; 8000 sinon.
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers --forwarded-allow-ips='*'"]
