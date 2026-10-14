"""LLM : texte de leçon → cartes de révision.

Confidentialité : on n'envoie au LLM que le texte de la leçon, jamais le pseudo ni l'id.
"""

import logging
import random
import re
import unicodedata
from typing import Literal

from openai import OpenAI
from pydantic import BaseModel

from app.config import settings

ASKED_CARDS = 12  # on en demande plus : certaines seront écartées par clean_card
MAX_CARDS = 10
MAX_QUESTION_WORDS = 15
MAX_BLANK_WORDS = 2
BLANK = "___"
VRAI_FAUX = ("Vrai", "Faux")

logger = logging.getLogger(__name__)


class CardDraft(BaseModel):
    type: Literal["qcm", "vrai_faux", "trou"]
    question: str
    answer: str
    choices: list[str]
    explanation: str


class Deck(BaseModel):
    cards: list[CardDraft]


class GenerationError(Exception):
    """Le LLM n'a pas répondu ou a refusé."""


DECK_PROMPT = f"""Tu crées des cartes de révision pour un collégien (11-15 ans) qui a un TDAH ou un trouble dys.
À partir de la leçon fournie, crée {ASKED_CARDS} cartes.

Règles :
- Une seule idée par carte.
- Question de {MAX_QUESTION_WORDS} mots maximum, simple et directe. Vocabulaire de collège.
- Explication : une seule phrase courte qui aide à retenir.
- Utilise UNIQUEMENT des informations présentes dans la leçon. Si une information manque, ne fais pas de carte.
- Mélange les trois types :
  - "qcm" : exactement 4 choix dans "choices", dont la bonne réponse recopiée à l'identique dans "answer".
    Les 3 distracteurs sont plausibles et de même longueur que la bonne réponse,
    mais clairement faux d'après la leçon : un seul choix doit pouvoir être juste.
  - "vrai_faux" : "question" est une affirmation. "answer" vaut exactement "Vrai" ou "Faux". "choices" est vide.
    Fais-en environ la moitié fausses.
  - "trou" : "question" est une phrase de la leçon où le mot-clé est remplacé par {BLANK}.
    "answer" est le mot manquant (un ou deux mots). "choices" est vide.
- Tutoiement, ton neutre, pas de « Bravo ».
"""


def normalize(text: str) -> str:
    """Pour comparer des réponses : minuscules, sans accents, espaces réduits. « Élève » == « eleve »."""
    decomposed = unicodedata.normalize("NFD", text.casefold())
    without_accents = "".join(c for c in decomposed if unicodedata.category(c) != "Mn")
    return " ".join(without_accents.split()).strip(" .!?;:")


def count_words(text: str) -> int:
    # « l'atome » compte pour un mot, la ponctuation isolée (« ? ») pour zéro.
    return len(re.findall(r"\w[\w'’-]*", text))


def clean_card(draft: CardDraft) -> CardDraft | None:
    """Remet une carte en forme, ou renvoie None si elle ne respecte pas les règles."""
    question = " ".join(draft.question.split())
    answer = draft.answer.strip()
    explanation = draft.explanation.strip()
    choices: list[str] = []

    if not question or not answer or not explanation or count_words(question) > MAX_QUESTION_WORDS:
        return None

    if draft.type == "qcm":
        choices = list(dict.fromkeys(c.strip() for c in draft.choices if c.strip()))
        matching = [c for c in choices if normalize(c) == normalize(answer)]
        if len(choices) != 4 or len(matching) != 1:
            return None
        answer = matching[0]
        random.shuffle(choices)  # le LLM met souvent la bonne réponse en premier
    elif draft.type == "vrai_faux":
        answer = next((v for v in VRAI_FAUX if normalize(v) == normalize(answer)), "")
        if not answer:
            return None
    else:  # trou
        if question.count(BLANK) != 1 or count_words(answer) > MAX_BLANK_WORDS:
            return None

    return CardDraft(type=draft.type, question=question, answer=answer, choices=choices, explanation=explanation)


def clean_deck(deck: Deck) -> list[CardDraft]:
    cards = [card for draft in deck.cards if (card := clean_card(draft))]
    if len(cards) < len(deck.cards):
        logger.info("%d carte(s) écartée(s) sur %d", len(deck.cards) - len(cards), len(deck.cards))
    return cards[:MAX_CARDS]


def get_client() -> OpenAI:
    # Timeout explicite : par défaut le SDK peut attendre 10 min, l'ado ne doit jamais rester bloqué.
    return OpenAI(api_key=settings.openai_api_key or None, timeout=60, max_retries=1)


def generate_deck(lesson_text: str) -> list[CardDraft]:
    """Appelle le LLM (sortie structurée Pydantic) et renvoie les cartes valides."""
    try:
        completion = get_client().chat.completions.parse(
            model=settings.llm_model,
            temperature=0.2,
            messages=[
                {"role": "system", "content": DECK_PROMPT},
                {"role": "user", "content": f"Leçon :\n\n{lesson_text}"},
            ],
            response_format=Deck,
        )
    except Exception as error:  # réseau, quota, clé invalide…
        raise GenerationError(str(error)) from error

    deck = completion.choices[0].message.parsed
    if deck is None:
        raise GenerationError("Réponse vide ou refus du modèle")
    return clean_deck(deck)
