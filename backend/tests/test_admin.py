from collections.abc import Callable
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.config import settings
from app.models import Card, Lesson, Review, User
from app.routers.admin import session_starts
from tests.helpers import Clock

# Jeudi 15 octobre 2026, 18h à Paris. Semaine du lundi 12.
NOW = datetime(2026, 10, 15, 16, 0, tzinfo=UTC)


@pytest.fixture
def admin(make_client: Callable[[str], TestClient], monkeypatch: pytest.MonkeyPatch, clock: Clock) -> TestClient:
    monkeypatch.setattr(settings, "admin_pseudos", "Teddy, autre_admin")
    clock.now = NOW
    return make_client("teddy")


def add_reviews(session: Session, pseudo: str, *moments: datetime) -> None:
    user = User(pseudo=pseudo, password_hash="!", created_at=NOW - timedelta(days=30))
    session.add(user)
    session.commit()
    lesson = Lesson(user_id=user.id, title="L", text="Une leçon.")  # type: ignore[arg-type]
    session.add(lesson)
    session.commit()
    card = Card(lesson_id=lesson.id, type="trou", question="q ___", answer="a", explanation="e")  # type: ignore[arg-type]
    session.add(card)
    session.commit()
    for moment in moments:
        session.add(Review(card_id=card.id, user_id=user.id, correct=True, reviewed_at=moment))  # type: ignore[arg-type]
    session.commit()


def test_reponses_proches_meme_seance() -> None:
    t = NOW
    starts = session_starts([t, t + timedelta(minutes=2), t + timedelta(minutes=29), t + timedelta(hours=2)])
    assert starts == [t, t + timedelta(hours=2)]


def test_reserve_aux_admins(client: TestClient, clock: Clock) -> None:
    assert client.get("/admin/stats").status_code == 404  # alice n'est pas admin


def test_statistiques_de_la_semaine(admin: TestClient, session: Session) -> None:
    monday = datetime(2026, 10, 12, 8, 0, tzinfo=UTC)
    # Assidue : 3 séances cette semaine (dont 2 réponses dans la même séance)
    add_reviews(session, "assidue", monday, monday + timedelta(minutes=5), monday + timedelta(days=1), NOW)
    # Occasionnel : 1 séance cette semaine, 1 la semaine d'avant
    add_reviews(session, "occasionnel", monday + timedelta(days=2), monday - timedelta(days=3))

    stats = admin.get("/admin/stats?weeks=2").json()
    this_week, last_week = stats["weeks"]

    assert this_week["week_start"] == "2026-10-12"
    assert this_week["registered"] == 3  # teddy, assidue, occasionnel
    assert (this_week["active"], this_week["sessions"]) == (2, 4)
    assert this_week["sessions_per_active"] == 2.0
    assert this_week["pct_3plus"] == 33.3  # 1 inscrit sur 3
    assert (last_week["active"], last_week["sessions"]) == (1, 1)

    by_pseudo = {u["pseudo"]: u for u in stats["users"]}
    assert by_pseudo["assidue"]["sessions_this_week"] == 3
    assert by_pseudo["occasionnel"]["sessions_total"] == 2
    assert by_pseudo["teddy"]["last_session"] is None


def test_semaine_a_l_heure_de_paris(admin: TestClient, session: Session) -> None:
    # Dimanche 11 octobre, 22h30 UTC = lundi 12, 00h30 à Paris → compte pour la semaine du 12
    add_reviews(session, "noctambule", datetime(2026, 10, 11, 22, 30, tzinfo=UTC))
    this_week = admin.get("/admin/stats?weeks=1").json()["weeks"][0]
    assert this_week["sessions"] == 1
