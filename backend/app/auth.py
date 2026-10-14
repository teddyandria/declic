from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, select

from app.db import get_session
from app.models import User

LOCAL_PSEUDO = "local"


def current_user(session: Annotated[Session, Depends(get_session)]) -> User:
    """Provisoire jusqu'à la phase 6 (JWT) : tout le monde est l'utilisateur « local »."""
    user = session.exec(select(User).where(User.pseudo == LOCAL_PSEUDO)).first()
    if user is None:
        user = User(pseudo=LOCAL_PSEUDO, password_hash="!")
        session.add(user)
        session.commit()
        session.refresh(user)
    return user


CurrentUser = Annotated[User, Depends(current_user)]
SessionDep = Annotated[Session, Depends(get_session)]
