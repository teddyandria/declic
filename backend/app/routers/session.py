from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import select

from app.auth import CurrentUser, SessionDep
from app.generate import normalize
from app.models import Card, Lesson, Review
from app.routers.cards import get_owned_card
from app.routers.lessons import get_owned_lesson
from app.scheduler import pick_session_cards, review, utc_now
from app.schemas import ReviewCreate, ReviewResult, SessionCard

router = APIRouter(tags=["session"])

NowDep = Annotated[datetime, Depends(utc_now)]


@router.get("/session")
def get_session_cards(
    session: SessionDep, user: CurrentUser, now: NowDep, lesson_id: int | None = None
) -> list[SessionCard]:
    """Les cartes de la séance (toutes leçons, ou une seule avec ?lesson_id=)."""
    query = select(Card).join(Lesson).where(Lesson.user_id == user.id)
    if lesson_id is not None:
        get_owned_lesson(session, lesson_id, user)  # 404 si pas à lui
        query = query.where(Card.lesson_id == lesson_id)
    cards = pick_session_cards(list(session.exec(query).all()), now)
    return [
        SessionCard(id=c.id, type=c.type, question=c.question, choices=c.choices, lesson_title=c.lesson.title)  # type: ignore[arg-type]
        for c in cards
    ]


@router.post("/reviews")
def create_review(body: ReviewCreate, session: SessionDep, user: CurrentUser, now: NowDep) -> ReviewResult:
    """Corrige côté serveur (le client ne connaît pas la réponse) et met à jour FSRS."""
    card = get_owned_card(session, body.card_id, user)
    correct = normalize(body.answer) == normalize(card.answer)

    card.fsrs_state = review(card.fsrs_state, correct, now)
    session.add(card)
    session.add(Review(card_id=card.id, user_id=user.id, correct=correct, reviewed_at=now))  # type: ignore[arg-type]
    session.commit()
    return ReviewResult(correct=correct, answer=card.answer, explanation=card.explanation)
