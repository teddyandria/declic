"""Alembic : applique les migrations sur la base de DATABASE_URL.

    uv run alembic upgrade head                              # met la base à jour
    uv run alembic revision --autogenerate -m "ajout de …"   # après un changement dans models.py
"""

from logging.config import fileConfig

from alembic import context
from sqlmodel import SQLModel

from app import models  # noqa: F401  (enregistre les tables dans SQLModel.metadata)
from app.config import settings
from app.db import make_engine

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata


def database_url() -> str:
    # Un test peut imposer sa base via la config Alembic ; sinon, celle de l'app.
    return config.get_main_option("sqlalchemy.url") or settings.database_url


def run_migrations_offline() -> None:
    """Génère le SQL sans se connecter (alembic upgrade head --sql)."""
    context.configure(url=database_url(), target_metadata=target_metadata, literal_binds=True, render_as_batch=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    engine = make_engine(database_url())
    with engine.connect() as connection:
        # render_as_batch : SQLite ne sait pas modifier une colonne, Alembic recrée alors la table.
        context.configure(connection=connection, target_metadata=target_metadata, render_as_batch=True)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
