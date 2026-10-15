from datetime import timedelta

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models import Card, Lesson, User
from tests.helpers import T0, Clock, make_lesson


def test_session_ne_renvoie_jamais_la_reponse(client: TestClient, session: Session, clock: Clock) -> None:
    make_lesson(client, session, 3)
    cards = client.get("/session").json()
    assert len(cards) == 3
    assert cards[0]["lesson_title"] == "Volcans"
    for card in cards:
        assert "answer" not in card and "explanation" not in card
        assert "Réponse" not in str(card)


def test_session_max_10_cartes(client: TestClient, session: Session, clock: Clock) -> None:
    make_lesson(client, session, 14)
    assert len(client.get("/session").json()) == 10


def test_correction_normalisee(client: TestClient, session: Session, clock: Clock) -> None:
    make_lesson(client, session, 1)
    card_id = client.get("/session").json()[0]["id"]
    result = client.post("/reviews", json={"card_id": card_id, "answer": "  REPONSE 0 "}).json()
    assert result == {"correct": True, "answer": "Réponse 0", "explanation": "Explication 0", "xp_gained": 10}


def test_mauvaise_reponse_renvoie_la_bonne(client: TestClient, session: Session, clock: Clock) -> None:
    make_lesson(client, session, 1)
    card_id = client.get("/session").json()[0]["id"]
    result = client.post("/reviews", json={"card_id": card_id, "answer": "n'importe quoi"}).json()
    assert result["correct"] is False
    assert result["answer"] == "Réponse 0"


def test_carte_ratee_revient_avant_carte_reussie(client: TestClient, session: Session, clock: Clock) -> None:
    make_lesson(client, session, 2)
    first, second = client.get("/session").json()
    client.post("/reviews", json={"card_id": first["id"], "answer": "Réponse 0"})  # juste
    client.post("/reviews", json={"card_id": second["id"], "answer": "faux"})  # raté

    # Juste après la séance : plus rien n'est dû
    assert client.get("/session").json() == []

    # 5 minutes plus tard : seule la carte ratée est revenue
    clock.now = T0 + timedelta(minutes=5)
    assert [c["id"] for c in client.get("/session").json()] == [second["id"]]

    # Le lendemain : les deux sont dues, la ratée passe en premier
    clock.now = T0 + timedelta(days=1)
    assert [c["id"] for c in client.get("/session").json()] == [second["id"], first["id"]]


def test_review_enregistree(client: TestClient, session: Session, clock: Clock) -> None:
    make_lesson(client, session, 1)
    card_id = client.get("/session").json()[0]["id"]
    client.post("/reviews", json={"card_id": card_id, "answer": "Réponse 0"})
    card = session.get(Card, card_id)
    assert card is not None and card.fsrs_state is not None
    assert [r.correct for r in card.reviews] == [True]


def test_session_par_lecon(client: TestClient, session: Session, clock: Clock) -> None:
    volcans = make_lesson(client, session, 2)
    make_lesson(client, session, 3)
    cards = client.get(f"/session?lesson_id={volcans}").json()
    assert len(cards) == 2
    assert client.get("/session?lesson_id=999").status_code == 404


def test_review_carte_inconnue_404(client: TestClient, clock: Clock) -> None:
    assert client.post("/reviews", json={"card_id": 999, "answer": "x"}).status_code == 404


def test_review_carte_d_un_autre_utilisateur_404(client: TestClient, session: Session, clock: Clock) -> None:
    other = User(pseudo="autre", password_hash="!")
    session.add(other)
    session.commit()
    lesson = Lesson(user_id=other.id, title="Secret", text="Leçon d'un autre utilisateur.")  # type: ignore[arg-type]
    session.add(lesson)
    session.commit()
    card = Card(lesson_id=lesson.id, type="trou", question="q ___", answer="a", explanation="e")  # type: ignore[arg-type]
    session.add(card)
    session.commit()

    assert client.get("/session").json() == []
    assert client.post("/reviews", json={"card_id": card.id, "answer": "a"}).status_code == 404
