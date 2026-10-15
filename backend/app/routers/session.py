from datetime import timedelta

from fastapi import APIRouter, HTTPException, status
from sqlmodel import col, select

from app.auth import CurrentUser, SessionDep
from app.game import XP_SESSION_END, current_streak, level_info, next_streak, paris_today, xp_for_answer
from app.generate import normalize
from app.models import Card, Lesson, Review
from app.routers.cards import get_owned_card
from app.routers.lessons import get_owned_lesson
from app.routers.me import get_player
from app.scheduler import NowDep, pick_session_cards, review
from app.schemas import FinishResult, ReviewCreate, ReviewResult, SessionCard

router = APIRouter(tags=["session"])


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
    """Corrige côté serveur (le client ne connaît pas la réponse), met à jour FSRS et l'XP."""
    card = get_owned_card(session, body.card_id, user)
    correct = normalize(body.answer) == normalize(card.answer)
    xp_gained = xp_for_answer(correct)

    card.fsrs_state = review(card.fsrs_state, correct, now)
    player = get_player(session, user)
    player.xp += xp_gained
    session.add_all([card, player, Review(card_id=card.id, user_id=user.id, correct=correct, reviewed_at=now)])  # type: ignore[arg-type]
    session.commit()
    return ReviewResult(correct=correct, answer=card.answer, explanation=card.explanation, xp_gained=xp_gained)


@router.post("/session/finish")
def finish_session(session: SessionDep, user: CurrentUser, now: NowDep) -> FinishResult:
    """Bonus de fin et série. Il faut avoir répondu à au moins une carte dans l'heure."""
    recent = session.exec(
        select(Review).where(Review.user_id == user.id, col(Review.reviewed_at) >= now - timedelta(hours=1))
    ).first()
    if recent is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Réponds d'abord à au moins une carte.")

    player = get_player(session, user)
    today = paris_today(now)
    level_before = level_info(player.xp).level
    streak_before = current_streak(player.streak, player.last_played_date, today)

    player.xp += XP_SESSION_END
    player.streak = next_streak(player.streak, player.last_played_date, today)
    player.last_played_date = today
    session.add(player)
    session.commit()

    info = level_info(player.xp)
    return FinishResult(
        xp_gained=XP_SESSION_END,
        xp=player.xp,
        level=info.level,
        xp_into_level=info.xp_into_level,
        xp_for_next=info.xp_for_next,
        streak=player.streak,
        level_up=info.level > level_before,
        streak_extended=player.streak > streak_before,
    )
