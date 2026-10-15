import os

# Avant d'importer l'app : la config exige un secret JWT.
os.environ.setdefault("JWT_SECRET", "secret-de-test-assez-long-pour-pyjwt-0123456789")

from collections.abc import Callable, Iterator  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlmodel import Session, SQLModel, create_engine  # noqa: E402

from app.db import get_session, make_engine  # noqa: E402
from app.main import app  # noqa: E402
from app.scheduler import utc_now  # noqa: E402
from tests.helpers import Clock  # noqa: E402

PASSWORD = "motdepasse123"


# Par défaut : SQLite en mémoire (rapide). Pour rejouer la suite sur Postgres :
#   TEST_DATABASE_URL=postgresql://declic:declic@localhost:5433/declic_test uv run pytest
TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")


@pytest.fixture
def session() -> Iterator[Session]:
    """Base neuve pour chaque test."""
    if TEST_DATABASE_URL:
        engine = make_engine(TEST_DATABASE_URL)
        SQLModel.metadata.drop_all(engine)
    else:
        from sqlalchemy.pool import StaticPool

        engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()


@pytest.fixture
def anonymous(session: Session) -> Iterator[TestClient]:
    """Client sans compte."""
    app.dependency_overrides[get_session] = lambda: session
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def make_client(anonymous: TestClient) -> Callable[[str], TestClient]:
    """Crée un compte et renvoie un client connecté avec ce compte."""

    def make(pseudo: str) -> TestClient:
        response = anonymous.post("/auth/register", json={"pseudo": pseudo, "password": PASSWORD, "consent": True})
        assert response.status_code == 201, response.text
        token = response.json()["access_token"]
        return TestClient(app, headers={"Authorization": f"Bearer {token}"})

    return make


@pytest.fixture
def client(make_client: Callable[[str], TestClient]) -> TestClient:
    """Client connecté en tant qu'« alice »."""
    return make_client("alice")


@pytest.fixture
def other_client(make_client: Callable[[str], TestClient]) -> TestClient:
    """Client connecté en tant que « bob »."""
    return make_client("bob")


@pytest.fixture
def clock(anonymous: TestClient) -> Iterator[Clock]:
    """Fige l'heure de l'API ; un test la fait avancer avec `clock.now = …`."""
    clock = Clock()
    app.dependency_overrides[utc_now] = lambda: clock.now
    yield clock
