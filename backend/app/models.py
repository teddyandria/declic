from datetime import UTC, date, datetime
from typing import Any, Literal

from sqlalchemy import JSON, Column, DateTime
from sqlmodel import Field, Relationship, SQLModel

CardType = Literal["qcm", "vrai_faux", "trou"]


def now_utc() -> datetime:
    return datetime.now(UTC)


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    pseudo: str = Field(unique=True, index=True, max_length=30)
    password_hash: str
    created_at: datetime = Field(default_factory=now_utc, sa_type=DateTime(timezone=True))  # type: ignore[call-overload]
    consent_ok: bool = False


class Lesson(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    title: str = Field(max_length=120)
    text: str
    created_at: datetime = Field(default_factory=now_utc, sa_type=DateTime(timezone=True))  # type: ignore[call-overload]

    cards: list["Card"] = Relationship(back_populates="lesson", cascade_delete=True)


class Card(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    lesson_id: int = Field(foreign_key="lesson.id", index=True, ondelete="CASCADE")
    type: str  # CardType ; str en base, validé à l'entrée
    question: str
    answer: str
    choices: list[str] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
    explanation: str
    # État FSRS sérialisé (rempli en phase 3)
    fsrs_state: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=now_utc, sa_type=DateTime(timezone=True))  # type: ignore[call-overload]

    lesson: Lesson = Relationship(back_populates="cards")
    reviews: list["Review"] = Relationship(back_populates="card", cascade_delete=True)


class Review(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    card_id: int = Field(foreign_key="card.id", index=True, ondelete="CASCADE")
    user_id: int = Field(foreign_key="user.id", index=True)
    correct: bool
    reviewed_at: datetime = Field(default_factory=now_utc, sa_type=DateTime(timezone=True))  # type: ignore[call-overload]

    card: Card = Relationship(back_populates="reviews")


class Player(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    xp: int = 0
    streak: int = 0
    last_played_date: date | None = None
