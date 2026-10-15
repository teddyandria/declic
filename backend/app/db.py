from collections.abc import Iterator

from sqlalchemy import Engine
from sqlmodel import Session, create_engine

from app.config import settings


def normalize_url(url: str) -> str:
    """Les hébergeurs donnent `postgres://…` ou `postgresql://…` ; SQLAlchemy doit savoir qu'on utilise psycopg 3."""
    for prefix in ("postgres://", "postgresql://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url.removeprefix(prefix)
    return url


def make_engine(url: str) -> Engine:
    url = normalize_url(url)
    # check_same_thread : SQLite refuse sinon d'être utilisé depuis les threads de FastAPI.
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    # pool_pre_ping : vérifie la connexion avant usage (Postgres coupe les connexions inactives).
    return create_engine(url, connect_args=connect_args, pool_pre_ping=True)


engine = make_engine(settings.database_url)


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
