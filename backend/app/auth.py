from typing import Annotated

from fastapi import Depends
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.db import get_session
from app.models import User

LOCAL_PSEUDO = "local"


def current_user(session: Annotated[Session, Depends(get_session)]) -> User:
    """Provisoire jusqu'à la phase 6 (JWT) : tout le monde est l'utilisateur « local »."""
    query = select(User).where(User.pseudo == LOCAL_PSEUDO)
    user = session.exec(query).first()
    if user is None:
        try:
            user = User(pseudo=LOCAL_PSEUDO, password_hash="!")
            session.add(user)
            session.commit()
            session.refresh(user)
        except IntegrityError:  # une requête parallèle l'a créé juste avant nous
            session.rollback()
            user = session.exec(query).one()
    return user


CurrentUser = Annotated[User, Depends(current_user)]
SessionDep = Annotated[Session, Depends(get_session)]
