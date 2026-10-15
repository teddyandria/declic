"""Comptes pseudo + mot de passe (sans e-mail) et jetons JWT."""

from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pwdlib import PasswordHash
from sqlalchemy import func
from sqlmodel import Session, select

from app.config import settings
from app.db import get_session
from app.models import User
from app.schemas import RegisterBody, Token

ALGORITHM = "HS256"

password_hash = PasswordHash.recommended()  # argon2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)  # 401 géré par nous, en français

SessionDep = Annotated[Session, Depends(get_session)]

router = APIRouter(prefix="/auth", tags=["auth"])


def create_token(user: User) -> Token:
    expires = datetime.now(UTC) + timedelta(days=settings.jwt_expire_days)
    token = jwt.encode({"sub": str(user.id), "exp": expires}, settings.jwt_secret, algorithm=ALGORITHM)
    return Token(access_token=token)


def find_by_pseudo(session: Session, pseudo: str) -> User | None:
    # « Lea » et « lea » sont le même compte
    return session.exec(select(User).where(func.lower(User.pseudo) == pseudo.lower())).first()


def current_user(token: Annotated[str | None, Depends(oauth2_scheme)], session: SessionDep) -> User:
    unauthorized = HTTPException(
        status.HTTP_401_UNAUTHORIZED, "Reconnecte-toi.", headers={"WWW-Authenticate": "Bearer"}
    )
    if token is None:
        raise unauthorized
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
        user = session.get(User, int(payload["sub"]))
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise unauthorized
    if user is None:  # compte supprimé depuis
        raise unauthorized
    return user


CurrentUser = Annotated[User, Depends(current_user)]


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(body: RegisterBody, session: SessionDep) -> Token:
    if find_by_pseudo(session, body.pseudo):
        raise HTTPException(status.HTTP_409_CONFLICT, "Ce pseudo est déjà pris.")
    user = User(pseudo=body.pseudo, password_hash=password_hash.hash(body.password), consent_ok=body.consent)
    session.add(user)
    session.commit()
    session.refresh(user)
    return create_token(user)


@router.post("/login")
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep) -> Token:
    user = find_by_pseudo(session, form.username.strip())
    # Même message que le pseudo existe ou non : on ne révèle pas quels pseudos sont pris.
    if user is None or not password_hash.verify(form.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Pseudo ou mot de passe incorrect.")
    return create_token(user)
