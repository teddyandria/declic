from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models import Card, Lesson, Player, Review, User
from tests.conftest import PASSWORD
from tests.helpers import make_lesson


def register(anonymous: TestClient, pseudo: str, **overrides: object) -> int:
    body = {"pseudo": pseudo, "password": PASSWORD, "consent": True} | overrides
    return anonymous.post("/auth/register", json=body).status_code


def login(anonymous: TestClient, pseudo: str, password: str = PASSWORD) -> int:
    return anonymous.post("/auth/login", data={"username": pseudo, "password": password}).status_code


def test_inscription_puis_connexion(anonymous: TestClient) -> None:
    assert register(anonymous, "Lea_92") == 201
    assert login(anonymous, "Lea_92") == 200
    assert login(anonymous, "lea_92") == 200  # pseudo insensible à la casse


def test_mot_de_passe_stocke_hache(anonymous: TestClient, session: Session) -> None:
    register(anonymous, "lea")
    user = session.exec(select(User)).one()
    assert PASSWORD not in user.password_hash
    assert user.password_hash.startswith("$argon2")
    assert user.consent_ok is True


def test_pseudo_deja_pris(anonymous: TestClient) -> None:
    register(anonymous, "lea")
    assert register(anonymous, "LEA") == 409


def test_consentement_obligatoire(anonymous: TestClient) -> None:
    assert register(anonymous, "lea", consent=False) == 422
    assert register(anonymous, "lea", consent=None) == 422


def test_pseudo_et_mot_de_passe_valides(anonymous: TestClient) -> None:
    assert register(anonymous, "le") == 422  # trop court
    assert register(anonymous, "léa ") == 422  # accents et espaces refusés
    assert register(anonymous, "lea", password="court") == 422


def test_mauvais_mot_de_passe(anonymous: TestClient) -> None:
    register(anonymous, "lea")
    assert login(anonymous, "lea", "pas-le-bon") == 401
    assert login(anonymous, "inconnu") == 401


def test_routes_protegees(anonymous: TestClient) -> None:
    for method, path in [("GET", "/lessons"), ("GET", "/session"), ("GET", "/me"), ("DELETE", "/me")]:
        assert anonymous.request(method, path).status_code == 401
    bad = anonymous.get("/me", headers={"Authorization": "Bearer pas-un-jeton"})
    assert bad.status_code == 401


def test_b_recoit_404_sur_les_donnees_de_a(client: TestClient, other_client: TestClient, session: Session) -> None:
    lesson_id = make_lesson(client, session, 1)
    card_id = client.get(f"/lessons/{lesson_id}").json()["cards"][0]["id"]

    assert other_client.get("/lessons").json() == []
    assert other_client.get("/session").json() == []
    for method, path, body in [
        ("GET", f"/lessons/{lesson_id}", None),
        ("DELETE", f"/lessons/{lesson_id}", None),
        ("POST", f"/lessons/{lesson_id}/generate", None),
        ("GET", f"/session?lesson_id={lesson_id}", None),
        ("PATCH", f"/cards/{card_id}", {"explanation": "piraté"}),
        ("DELETE", f"/cards/{card_id}", None),
        ("POST", "/reviews", {"card_id": card_id, "answer": "x"}),
    ]:
        response = other_client.request(method, path, json=body)
        assert response.status_code == 404, f"{method} {path} → {response.status_code}"

    # Et rien n'a bougé chez A
    assert client.get(f"/lessons/{lesson_id}").json()["cards"][0]["explanation"] == "Explication 0"


def test_supprimer_son_compte_efface_tout(client: TestClient, other_client: TestClient, session: Session) -> None:
    lesson_id = make_lesson(client, session, 2)
    card_id = client.get(f"/lessons/{lesson_id}").json()["cards"][0]["id"]
    client.post("/reviews", json={"card_id": card_id, "answer": "Réponse 0"})
    make_lesson(other_client, session, 1, title="Leçon de Bob")

    assert client.delete("/me").status_code == 204

    assert session.exec(select(User).where(User.pseudo == "alice")).first() is None
    assert len(session.exec(select(Lesson)).all()) == 1  # il ne reste que celle de Bob
    assert len(session.exec(select(Card)).all()) == 1
    assert session.exec(select(Review)).all() == []
    assert session.exec(select(Player)).all() == []
    assert client.get("/me").status_code == 401  # l'ancien jeton ne marche plus
    assert other_client.get("/lessons").json()[0]["title"] == "Leçon de Bob"
