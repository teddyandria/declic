from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlmodel import Session

from tests.helpers import T0, Clock, make_lesson


def play(client: TestClient, answers_right: int, answers_wrong: int = 0) -> dict[str, object]:
    """Joue une séance (les premières cartes justes, les suivantes fausses) puis la termine."""
    cards = client.get("/session").json()
    for i, card in enumerate(cards[: answers_right + answers_wrong]):
        answer = card["question"].replace("Question", "Réponse").replace(" ___", "") if i < answers_right else "?"
        client.post("/reviews", json={"card_id": card["id"], "answer": answer})
    return client.post("/session/finish").json()


def test_xp_juste_faux_et_fin(client: TestClient, session: Session, clock: Clock) -> None:
    make_lesson(client, session, 3)
    result = play(client, answers_right=2, answers_wrong=1)
    assert result["xp_gained"] == 20
    assert result["xp"] == 10 + 10 + 2 + 20
    assert client.get("/me").json()["xp"] == 42


def test_fin_sans_reponse_refusee(client: TestClient, clock: Clock) -> None:
    assert client.post("/session/finish").status_code == 409


def test_serie_sur_plusieurs_jours(client: TestClient, session: Session, clock: Clock) -> None:
    make_lesson(client, session, 10)
    assert client.get("/me").json()["streak"] == 0

    first = play(client, 1)
    assert (first["streak"], first["streak_extended"]) == (1, True)

    again = play(client, 1)  # 2e séance le même jour
    assert (again["streak"], again["streak_extended"]) == (1, False)

    clock.now = T0 + timedelta(days=1)
    assert play(client, 1)["streak"] == 2

    clock.now = T0 + timedelta(days=3)  # un jour sauté
    assert client.get("/me").json()["streak"] == 0
    assert play(client, 1)["streak"] == 1


def test_serie_a_minuit_heure_de_paris(client: TestClient, session: Session, clock: Clock) -> None:
    make_lesson(client, session, 10)
    clock.now = datetime(2026, 10, 15, 21, 59, tzinfo=UTC)  # 23h59 à Paris
    assert play(client, 1)["streak"] == 1
    clock.now = datetime(2026, 10, 15, 22, 1, tzinfo=UTC)  # 00h01 le 16 à Paris
    assert play(client, 1)["streak"] == 2
    assert client.get("/me").json()["played_today"] is True


def test_passage_de_niveau(client: TestClient, session: Session, clock: Clock) -> None:
    make_lesson(client, session, 10)
    result = play(client, answers_right=8)  # 80 + 20 = 100 XP
    assert (result["level"], result["level_up"]) == (2, True)
    assert (result["xp_into_level"], result["xp_for_next"]) == (0, 150)


def test_maitrise_par_lecon(client: TestClient, session: Session, clock: Clock) -> None:
    lesson_id = make_lesson(client, session, 2)
    card_id = client.get("/session").json()[0]["id"]
    answer = client.get(f"/lessons/{lesson_id}").json()["cards"][0]["answer"]

    client.post("/reviews", json={"card_id": card_id, "answer": answer})
    assert client.get(f"/lessons/{lesson_id}").json()["mastered"] == 0  # 1re fois : encore en apprentissage

    clock.now = T0 + timedelta(minutes=15)
    client.post("/reviews", json={"card_id": card_id, "answer": answer})
    assert client.get(f"/lessons/{lesson_id}").json()["mastered"] == 1
    assert client.get("/me").json()["lessons"][0]["mastered"] == 1
