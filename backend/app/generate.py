"""LLM : texte de leçon → cartes de révision.

Confidentialité : on n'envoie au LLM que le texte de la leçon, jamais le pseudo ni l'id.
"""

import base64
import io
import logging
import random
import re
import unicodedata
from typing import Literal

from openai import OpenAI
from PIL import Image, ImageOps, UnidentifiedImageError
from pydantic import BaseModel

from app.config import settings

ASKED_CARDS = 12  # on en demande plus : certaines seront écartées par clean_card
MAX_CARDS = 10
MAX_QUESTION_WORDS = 15
MAX_BLANK_WORDS = 2
BLANK = "___"
VRAI_FAUX = ("Vrai", "Faux")
PHOTO_MAX_WIDTH = 1600

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


class InvalidImageError(Exception):
    """Le fichier envoyé n'est pas une image lisible."""


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


def request_deck(lesson_text: str) -> Deck:
    """Appel brut au LLM (sortie structurée Pydantic), avant tout nettoyage."""
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
    return deck


def generate_deck(lesson_text: str) -> list[CardDraft]:
    """Texte de la leçon → cartes valides, prêtes à enregistrer."""
    return clean_deck(request_deck(lesson_text))


PHOTO_PROMPT = """Cette photo montre une leçon (cahier, manuel ou fiche) d'un collégien.
Transcris fidèlement tout le texte de la leçon, dans l'ordre de lecture, sans résumer ni reformuler.
Garde les titres et les listes. Recolle les phrases coupées en fin de ligne du cahier. Ignore les gribouillages et les numéros de page.
Si aucun texte n'est lisible, réponds uniquement : AUCUN_TEXTE"""


def prepare_photo(data: bytes) -> bytes:
    """Redresse la photo (EXIF), la réduit à 1600 px de large max et la ré-encode en JPEG.

    Ré-encoder enlève aussi les métadonnées (position GPS du téléphone…) avant l'envoi au LLM.
    """
    try:
        image = Image.open(io.BytesIO(data))
        image = ImageOps.exif_transpose(image).convert("RGB")
    except (UnidentifiedImageError, OSError) as error:
        raise InvalidImageError from error
    if image.width > PHOTO_MAX_WIDTH:
        height = round(image.height * PHOTO_MAX_WIDTH / image.width)
        image = image.resize((PHOTO_MAX_WIDTH, height), Image.Resampling.LANCZOS)
    output = io.BytesIO()
    image.save(output, format="JPEG", quality=85)
    return output.getvalue()


def transcribe_photo(data: bytes) -> str:
    """Photo de leçon → texte. Renvoie "" si rien n'est lisible."""
    jpeg = base64.b64encode(prepare_photo(data)).decode()
    try:
        completion = get_client().chat.completions.create(
            model=settings.llm_vision_model,
            temperature=0,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": PHOTO_PROMPT},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{jpeg}"}},
                    ],
                }
            ],
        )
    except Exception as error:
        raise GenerationError(str(error)) from error

    text = (completion.choices[0].message.content or "").strip()
    return "" if "AUCUN_TEXTE" in text else text
