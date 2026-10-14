import pytest
from fastapi.testclient import TestClient

from app import generate
from app.generate import CardDraft, Deck, GenerationError, clean_deck, normalize

LESSON = {"title": "La cellule", "text": "La cellule est l'unité de base du vivant. Elle a un noyau."}


def qcm(**overrides: object) -> CardDraft:
    values: dict[str, object] = {
        "type": "qcm",
        "question": "Quelle est l'unité de base du vivant ?",
        "answer": "La cellule",
        "choices": ["La cellule", "L'atome", "Le tissu", "L'organe"],
        "explanation": "Tout être vivant est fait de cellules.",
    }
    return CardDraft.model_validate(values | overrides)


def test_normalize() -> None:
    assert normalize("Élève") == normalize("eleve")
    assert normalize("  La   Cellule. ") == "la cellule"


def test_qcm_valide_garde_ses_4_choix_melanges() -> None:
    [card] = clean_deck(Deck(cards=[qcm()]))
    assert sorted(card.choices) == sorted(qcm().choices)
    assert card.answer in card.choices


def test_qcm_reponse_absente_des_choix_ecarte() -> None:
    assert clean_deck(Deck(cards=[qcm(answer="Le virus")])) == []


def test_qcm_avec_3_choix_ecarte() -> None:
    assert clean_deck(Deck(cards=[qcm(choices=["La cellule", "L'atome", "Le tissu"])])) == []


def test_question_trop_longue_ecartee() -> None:
    long_question = " ".join(["mot"] * 16) + " ?"
    assert clean_deck(Deck(cards=[qcm(question=long_question)])) == []


def test_vrai_faux_normalise_la_reponse() -> None:
    draft = CardDraft(type="vrai_faux", question="La cellule a un noyau.", answer="vrai", choices=[], explanation="Oui.")
    [card] = clean_deck(Deck(cards=[draft]))
    assert card.answer == "Vrai"


def test_trou_sans_blanc_ou_reponse_longue_ecarte() -> None:
    ok = CardDraft(type="trou", question="La ___ est l'unité du vivant.", answer="cellule", choices=[], explanation="Base.")
    sans_blanc = ok.model_copy(update={"question": "La cellule est l'unité du vivant."})
    trop_long = ok.model_copy(update={"answer": "petite cellule ronde"})
    assert clean_deck(Deck(cards=[ok, sans_blanc, trop_long])) == [ok]


def test_route_generate_enregistre_les_cartes(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    sent: list[str] = []

    def fake_generate(text: str) -> list[CardDraft]:
        sent.append(text)
        return [qcm()] * 10

    monkeypatch.setattr("app.routers.lessons.generate_deck", fake_generate)
    lesson_id = client.post("/lessons", json=LESSON).json()["id"]

    response = client.post(f"/lessons/{lesson_id}/generate")
    assert response.status_code == 200
    assert len(response.json()["cards"]) == 10
    assert sent == [LESSON["text"]]  # seul le texte part au LLM

    # Régénérer remplace les cartes au lieu de les empiler
    client.post(f"/lessons/{lesson_id}/generate")
    assert len(client.get(f"/lessons/{lesson_id}").json()["cards"]) == 10


def test_route_generate_echec_llm_donne_502(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    def failing(_: str) -> list[CardDraft]:
        raise GenerationError("quota")

    monkeypatch.setattr("app.routers.lessons.generate_deck", failing)
    lesson_id = client.post("/lessons", json=LESSON).json()["id"]
    assert client.post(f"/lessons/{lesson_id}/generate").status_code == 502


def test_route_generate_lecon_inconnue_404(client: TestClient) -> None:
    assert client.post("/lessons/999/generate").status_code == 404


def test_generate_deck_n_envoie_que_le_texte(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    class FakeCompletions:
        def parse(self, **kwargs: object) -> object:
            captured.update(kwargs)
            message = type("M", (), {"parsed": Deck(cards=[qcm()])})
            return type("C", (), {"choices": [type("Ch", (), {"message": message})]})

    fake_client = type("Client", (), {"chat": type("Chat", (), {"completions": FakeCompletions()})})
    monkeypatch.setattr(generate, "get_client", lambda: fake_client)

    cards = generate.generate_deck("Texte de la leçon")
    assert len(cards) == 1
    assert captured["temperature"] == 0.2
    assert "Texte de la leçon" in str(captured["messages"])
