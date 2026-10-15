from datetime import UTC, datetime

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models import Card

T0 = datetime(2026, 10, 15, 16, 0, tzinfo=UTC)  # 18h à Paris


class Clock:
    """Horloge réglable injectée à la place de utc_now (voir la fixture `clock`)."""

    def __init__(self) -> None:
        self.now = T0


def make_lesson(client: TestClient, session: Session, n_cards: int, title: str = "Volcans") -> int:
    lesson_id: int = client.post("/lessons", json={"title": title, "text": "Un volcan crache de la lave."}).json()["id"]
    for i in range(n_cards):
        session.add(
            Card(lesson_id=lesson_id, type="trou", question=f"Question {i} ___", answer=f"Réponse {i}",
                 explanation=f"Explication {i}")
        )
    session.commit()
    return lesson_id
