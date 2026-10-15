# Déclic

Appli de révision gamifiée pour ados TDAH ou dys : photo ou texte de la leçon → ~10 questions → séance de 5 minutes.

## Lancer en dev

```bash
cp .env.example .env            # puis remplir OPENAI_API_KEY et JWT_SECRET

cd backend && uv sync && uv run alembic upgrade head          # crée / met à jour les tables
uv run uvicorn app.main:app --reload                            # http://localhost:8000/docs
cd frontend && npm install && npm run dev                       # http://localhost:5173
```

## Tout lancer comme en prod (Docker)

```bash
docker compose up --build       # http://localhost:8080 (Caddy → front + /api → FastAPI → Postgres)
docker compose up -d db         # seulement Postgres, sur localhost:5433
docker compose down             # arrêter (ajouter -v pour effacer la base)
```

## Modifier le schéma de la base

```bash
# après un changement dans backend/app/models.py :
cd backend && uv run alembic revision --autogenerate -m "ajout de …"   # relire le fichier généré !
uv run alembic upgrade head
```

En Docker et en prod, `alembic upgrade head` est lancé automatiquement au démarrage de l'API.

## Tests

```bash
cd backend && uv run pytest                     # SQLite en mémoire
docker compose up -d db && TEST_DATABASE_URL=postgresql://declic:declic@localhost:5433/declic_test uv run pytest
uv run python eval/run_eval.py                  # qualité des cartes générées → eval/out/
```
