"""Répétition espacée : on délègue tout à py-fsrs, on ne fait que (dé)sérialiser et trier.

Une carte jamais révisée a `fsrs_state = None` : c'est une « nouvelle » carte.
"""

from datetime import UTC, datetime
from typing import Annotated, Any

from fastapi import Depends

from fsrs import Card as FsrsCard
from fsrs import Rating, Scheduler, State

from app.models import Card

SESSION_SIZE = 10

scheduler = Scheduler()


def utc_now() -> datetime:
    """Dépendance FastAPI : les tests la remplacent pour faire avancer le temps."""
    return datetime.now(UTC)


NowDep = Annotated[datetime, Depends(utc_now)]


def review(fsrs_state: dict[str, Any] | None, correct: bool, now: datetime) -> dict[str, Any]:
    """Applique une réponse : juste → Good, faux → Again. Renvoie le nouvel état sérialisé."""
    card = FsrsCard.from_dict(fsrs_state) if fsrs_state else FsrsCard(due=now)  # type: ignore[arg-type]
    updated, _ = scheduler.review_card(card, Rating.Good if correct else Rating.Again, now)
    return updated.to_dict()


def due_date(fsrs_state: dict[str, Any]) -> datetime:
    return datetime.fromisoformat(fsrs_state["due"])


def is_mastered(fsrs_state: dict[str, Any] | None) -> bool:
    return fsrs_state is not None and fsrs_state["state"] == State.Review.value


def pick_session_cards(cards: list[Card], now: datetime, limit: int = SESSION_SIZE) -> list[Card]:
    """Les cartes dues d'abord (la plus en retard en premier), puis les nouvelles, `limit` au maximum.

    Les nouvelles viennent de la leçon la plus récente : c'est souvent celle du contrôle de demain.
    """
    due = sorted(
        (c for c in cards if c.fsrs_state and due_date(c.fsrs_state) <= now),
        key=lambda c: due_date(c.fsrs_state),  # type: ignore[arg-type]
    )
    new = sorted(
        (c for c in cards if c.fsrs_state is None),
        key=lambda c: (-c.lesson.created_at.timestamp(), c.id),
    )
    return (due + new)[:limit]
