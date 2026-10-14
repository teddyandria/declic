from fastapi import APIRouter, HTTPException, status
from sqlmodel import col, select

from app.auth import CurrentUser, SessionDep
from app.models import Lesson, User
from app.schemas import CardRead, LessonCreate, LessonDetail, LessonSummary

router = APIRouter(prefix="/lessons", tags=["lessons"])


def get_owned_lesson(session: SessionDep, lesson_id: int, user: User) -> Lesson:
    """404 si la leçon n'existe pas OU appartient à quelqu'un d'autre (on ne révèle pas qu'elle existe)."""
    lesson = session.get(Lesson, lesson_id)
    if lesson is None or lesson.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Leçon introuvable")
    return lesson


def to_detail(lesson: Lesson) -> LessonDetail:
    return LessonDetail(
        id=lesson.id,  # type: ignore[arg-type]
        title=lesson.title,
        text=lesson.text,
        created_at=lesson.created_at,
        cards=[CardRead.model_validate(card, from_attributes=True) for card in lesson.cards],
    )


@router.get("")
def list_lessons(session: SessionDep, user: CurrentUser) -> list[LessonSummary]:
    lessons = session.exec(
        select(Lesson).where(Lesson.user_id == user.id).order_by(col(Lesson.created_at).desc())
    ).all()
    return [
        LessonSummary(id=l.id, title=l.title, created_at=l.created_at, card_count=len(l.cards))  # type: ignore[arg-type]
        for l in lessons
    ]


@router.post("", status_code=status.HTTP_201_CREATED)
def create_lesson(body: LessonCreate, session: SessionDep, user: CurrentUser) -> LessonDetail:
    lesson = Lesson(user_id=user.id, title=body.title.strip(), text=body.text.strip())  # type: ignore[arg-type]
    session.add(lesson)
    session.commit()
    session.refresh(lesson)
    return to_detail(lesson)


@router.get("/{lesson_id}")
def read_lesson(lesson_id: int, session: SessionDep, user: CurrentUser) -> LessonDetail:
    return to_detail(get_owned_lesson(session, lesson_id, user))


@router.delete("/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lesson(lesson_id: int, session: SessionDep, user: CurrentUser) -> None:
    session.delete(get_owned_lesson(session, lesson_id, user))
    session.commit()
