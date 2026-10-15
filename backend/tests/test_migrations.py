"""Les migrations Alembic doivent produire exactement le schéma de models.py.

Si ce test échoue après un changement de modèle : uv run alembic revision --autogenerate -m "…"
"""

from pathlib import Path

from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.migration import MigrationContext
from sqlalchemy import create_engine, inspect
from sqlmodel import SQLModel

from app import models  # noqa: F401

BACKEND_DIR = Path(__file__).resolve().parents[1]


def alembic_config(url: str) -> Config:
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", url)
    return config


def test_migrations_a_jour_avec_les_modeles(tmp_path: Path) -> None:
    url = f"sqlite:///{tmp_path / 'migree.db'}"
    command.upgrade(alembic_config(url), "head")

    with create_engine(url).connect() as connection:
        differences = compare_metadata(MigrationContext.configure(connection), SQLModel.metadata)
    assert differences == [], f"Modèles modifiés sans migration : {differences}"


def test_migrations_reversibles(tmp_path: Path) -> None:
    url = f"sqlite:///{tmp_path / 'aller-retour.db'}"
    config = alembic_config(url)
    command.upgrade(config, "head")
    command.downgrade(config, "base")
    assert inspect(create_engine(url)).get_table_names() == ["alembic_version"]
