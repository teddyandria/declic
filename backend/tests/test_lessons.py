from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models import Card

LESSON = {"title": "La cellule", "text": "La cellule est l'unité de base du vivant. Elle a un noyau."}


def add_card(session: Session, lesson_id: int, **overrides: object) -> Card:
    card = Card(
        lesson_id=lesson_id,
        type="qcm",
        question="Quelle est l'unité de base du vivant ?",
        answer="La cellule",
        choices=["La cellule", "L'atome", "Le tissu", "L'organe"],
        explanation="Tout être vivant est fait de cellules.",
    )
    for key, value in overrides.items():
        setattr(card, key, value)
    session.add(card)
    session.commit()
    session.refresh(card)
    return card


def test_creer_lister_lire_supprimer(client: TestClient) -> None:
    created = client.post("/lessons", json=LESSON)
    assert created.status_code == 201
    lesson_id = created.json()["id"]

    listed = client.get("/lessons").json()
    assert [l["title"] for l in listed] == ["La cellule"]
    assert listed[0]["card_count"] == 0

    detail = client.get(f"/lessons/{lesson_id}").json()
    assert detail["text"] == LESSON["text"]
    assert detail["cards"] == []

    assert client.delete(f"/lessons/{lesson_id}").status_code == 204
    assert client.get(f"/lessons/{lesson_id}").status_code == 404


def test_lecon_inconnue_donne_404(client: TestClient) -> None:
    for response in (client.get("/lessons/999"), client.delete("/lessons/999")):
        assert response.status_code == 404
        assert response.json()["detail"] == "Leçon introuvable"


def test_lecon_trop_courte_refusee(client: TestClient) -> None:
    assert client.post("/lessons", json={"title": "x", "text": "trop court"}).status_code == 422


def test_supprimer_lecon_supprime_ses_cartes(client: TestClient, session: Session) -> None:
    lesson_id = client.post("/lessons", json=LESSON).json()["id"]
    card = add_card(session, lesson_id)
    client.delete(f"/lessons/{lesson_id}")
    session.expire_all()
    assert session.get(Card, card.id) is None


def test_modifier_carte(client: TestClient, session: Session) -> None:
    lesson_id = client.post("/lessons", json=LESSON).json()["id"]
    card = add_card(session, lesson_id)

    response = client.patch(f"/cards/{card.id}", json={"explanation": "Même les bactéries."})
    assert response.status_code == 200
    assert response.json()["explanation"] == "Même les bactéries."
    assert client.get(f"/lessons/{lesson_id}").json()["cards"][0]["explanation"] == "Même les bactéries."


def test_qcm_dont_la_reponse_n_est_pas_dans_les_choix_refuse(client: TestClient, session: Session) -> None:
    lesson_id = client.post("/lessons", json=LESSON).json()["id"]
    card = add_card(session, lesson_id)
    assert client.patch(f"/cards/{card.id}", json={"answer": "Le virus"}).status_code == 422


def test_supprimer_carte(client: TestClient, session: Session) -> None:
    lesson_id = client.post("/lessons", json=LESSON).json()["id"]
    card = add_card(session, lesson_id)
    assert client.delete(f"/cards/{card.id}").status_code == 204
    assert client.get(f"/lessons/{lesson_id}").json()["cards"] == []
    assert client.delete(f"/cards/{card.id}").status_code == 404
