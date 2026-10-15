"""Statistiques d'usage pour suivre le critère du MVP : ≥ la moitié des testeurs fait ≥ 3 séances par semaine.

Une « séance » est déduite des réponses : deux réponses à moins de 30 min d'écart sont dans la même séance.
"""

from collections import defaultdict
from datetime import date, datetime, timedelta

from fastapi import APIRouter, HTTPException, Query, status
from sqlmodel import col, select

from app.auth import CurrentUser, SessionDep
from app.config import settings
from app.game import paris_today
from app.models import Review, User
from app.scheduler import NowDep
from app.schemas import AdminStats, UserStats, WeekStats

router = APIRouter(prefix="/admin", tags=["admin"])

SESSION_GAP = timedelta(minutes=30)


def session_starts(times: list[datetime]) -> list[datetime]:
    """Heures de début des séances, à partir des heures de réponse triées."""
    starts: list[datetime] = []
    previous: datetime | None = None
    for moment in times:
        if previous is None or moment - previous > SESSION_GAP:
            starts.append(moment)
        previous = moment
    return starts


def week_start(day: date) -> date:
    return day - timedelta(days=day.weekday())


@router.get("/stats")
def stats(session: SessionDep, user: CurrentUser, now: NowDep, weeks: int = Query(4, ge=1, le=52)) -> AdminStats:
    if not settings.is_admin(user.pseudo):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not Found")  # comme une route qui n'existe pas

    users = session.exec(select(User).order_by(col(User.created_at))).all()
    times_by_user: dict[int, list[datetime]] = defaultdict(list)
    for user_id, reviewed_at in session.exec(select(Review.user_id, Review.reviewed_at).order_by(col(Review.reviewed_at))):
        times_by_user[user_id].append(reviewed_at)

    # Nombre de séances par (utilisateur, semaine)
    starts_by_user = {user_id: session_starts(times) for user_id, times in times_by_user.items()}
    per_week: dict[date, dict[int, int]] = defaultdict(lambda: defaultdict(int))
    for user_id, starts in starts_by_user.items():
        for start in starts:
            per_week[week_start(paris_today(start))][user_id] += 1

    this_week = week_start(paris_today(now))
    week_list: list[WeekStats] = []
    for i in range(weeks):
        monday = this_week - timedelta(weeks=i)
        week_end = monday + timedelta(days=7)
        registered = sum(1 for u in users if paris_today(u.created_at) < week_end)
        counts = per_week.get(monday, {})
        sessions = sum(counts.values())
        week_list.append(
            WeekStats(
                week_start=monday,
                registered=registered,
                active=len(counts),
                sessions=sessions,
                sessions_per_active=round(sessions / len(counts), 1) if counts else 0.0,
                pct_3plus=round(100 * sum(1 for n in counts.values() if n >= 3) / registered, 1) if registered else 0.0,
            )
        )

    user_list = [
        UserStats(
            pseudo=u.pseudo,
            created_at=u.created_at,
            sessions_total=len(starts_by_user.get(u.id, [])),  # type: ignore[arg-type]
            sessions_this_week=per_week.get(this_week, {}).get(u.id, 0),  # type: ignore[arg-type]
            last_session=(starts_by_user.get(u.id) or [None])[-1],  # type: ignore[arg-type]
        )
        for u in users
    ]
    return AdminStats(weeks=week_list, users=user_list)
