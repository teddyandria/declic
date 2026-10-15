from fastapi import APIRouter
from sqlmodel import Session

from app.auth import CurrentUser, SessionDep
from app.game import current_streak, level_info, paris_today
from app.models import Player, User
from app.routers.lessons import list_user_lessons
from app.scheduler import NowDep
from app.schemas import Me

router = APIRouter(tags=["me"])


def get_player(session: Session, user: User) -> Player:
    player = session.get(Player, user.id)
    if player is None:
        player = Player(user_id=user.id)  # type: ignore[arg-type]
        session.add(player)
    return player


@router.get("/me")
def read_me(session: SessionDep, user: CurrentUser, now: NowDep) -> Me:
    player = get_player(session, user)
    today = paris_today(now)
    info = level_info(player.xp)
    return Me(
        pseudo=user.pseudo,
        xp=player.xp,
        level=info.level,
        xp_into_level=info.xp_into_level,
        xp_for_next=info.xp_for_next,
        streak=current_streak(player.streak, player.last_played_date, today),
        played_today=player.last_played_date == today,
        lessons=list_user_lessons(session, user),
    )
