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
    mastered: int  # cartes en état FSRS « Review »


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
    mastered: int
    cards: list[CardRead]


class CardUpdate(BaseModel):
    question: str | None = Field(default=None, min_length=1, max_length=200)
    answer: str | None = Field(default=None, min_length=1, max_length=200)
    choices: list[str] | None = None
    explanation: str | None = Field(default=None, min_length=1, max_length=300)


class Transcription(BaseModel):
    text: str


class SessionCard(BaseModel):
    """Ce que voit l'ado pendant la séance : jamais la réponse ni l'explication."""

    id: int
    type: CardType
    question: str
    choices: list[str]
    lesson_title: str


class ReviewCreate(BaseModel):
    card_id: int
    answer: str = Field(max_length=200)


class ReviewResult(BaseModel):
    correct: bool
    answer: str
    explanation: str
    xp_gained: int


class Progress(BaseModel):
    """XP, niveau et série : ce qu'on affiche en gommettes."""

    xp: int
    level: int
    xp_into_level: int
    xp_for_next: int
    streak: int


class FinishResult(Progress):
    xp_gained: int
    level_up: bool
    streak_extended: bool


class Me(Progress):
    pseudo: str
    played_today: bool
    lessons: list[LessonSummary]
