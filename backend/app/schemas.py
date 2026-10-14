"""Formats d'entrée/sortie de l'API (distincts des tables pour ne jamais exposer user_id ou fsrs_state)."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.models import CardType


class LessonCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    text: str = Field(min_length=20, max_length=20_000)


class LessonSummary(BaseModel):
    id: int
    title: str
    created_at: datetime
    card_count: int


class CardRead(BaseModel):
    id: int
    type: CardType
    question: str
    answer: str
    choices: list[str]
    explanation: str


class LessonDetail(BaseModel):
    id: int
    title: str
    text: str
    created_at: datetime
    cards: list[CardRead]


class CardUpdate(BaseModel):
    question: str | None = Field(default=None, min_length=1, max_length=200)
    answer: str | None = Field(default=None, min_length=1, max_length=200)
    choices: list[str] | None = None
    explanation: str | None = Field(default=None, min_length=1, max_length=300)
