from fastapi import APIRouter, HTTPException, UploadFile, status
from sqlmodel import col, select

from app.auth import CurrentUser, SessionDep
from app.generate import GenerationError, InvalidImageError, generate_deck, transcribe_photo
from app.models import Card, Lesson, User
from app.scheduler import is_mastered
from app.schemas import CardRead, LessonCreate, LessonDetail, LessonSummary, Transcription

router = APIRouter(prefix="/lessons", tags=["lessons"])

MAX_PHOTO_BYTES = 15 * 1024 * 1024


def get_owned_lesson(session: SessionDep, lesson_id: int, user: User) -> Lesson:
    """404 si la leçon n'existe pas OU appartient à quelqu'un d'autre (on ne révèle pas qu'elle existe)."""
    lesson = session.get(Lesson, lesson_id)
    if lesson is None or lesson.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Leçon introuvable")
    return lesson


def mastered_count(lesson: Lesson) -> int:
    return sum(is_mastered(card.fsrs_state) for card in lesson.cards)


def to_summary(lesson: Lesson) -> LessonSummary:
    return LessonSummary(
        id=lesson.id,  # type: ignore[arg-type]
        title=lesson.title,
        created_at=lesson.created_at,
        card_count=len(lesson.cards),
        mastered=mastered_count(lesson),
    )


def list_user_lessons(session: SessionDep, user: User) -> list[LessonSummary]:
    lessons = session.exec(
        select(Lesson).where(Lesson.user_id == user.id).order_by(col(Lesson.created_at).desc())
    ).all()
    return [to_summary(lesson) for lesson in lessons]


def to_detail(lesson: Lesson) -> LessonDetail:
    return LessonDetail(
        id=lesson.id,  # type: ignore[arg-type]
        title=lesson.title,
        text=lesson.text,
        created_at=lesson.created_at,
        mastered=mastered_count(lesson),
        cards=[CardRead.model_validate(card, from_attributes=True) for card in lesson.cards],
    )


@router.get("")
def list_lessons(session: SessionDep, user: CurrentUser) -> list[LessonSummary]:
    return list_user_lessons(session, user)


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


@router.post("/{lesson_id}/generate")
def generate_cards(lesson_id: int, session: SessionDep, user: CurrentUser) -> LessonDetail:
    """Génère les cartes de la leçon. Remplace les cartes existantes (et leur progression)."""
    lesson = get_owned_lesson(session, lesson_id, user)
    try:
        drafts = generate_deck(lesson.text)
    except GenerationError:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "La génération a raté. Réessaie dans un instant.")
    if not drafts:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "Pas assez d'infos dans cette leçon pour faire des cartes.")

    for old in list(lesson.cards):
        session.delete(old)
    for draft in drafts:
        session.add(Card(lesson_id=lesson.id, **draft.model_dump()))  # type: ignore[arg-type]
    session.commit()
    session.refresh(lesson)
    return to_detail(lesson)


@router.post("/from-photo")
def lesson_from_photo(photo: UploadFile, _: CurrentUser) -> Transcription:
    """Photo → texte transcrit, que l'ado relit avant de créer la leçon. N'enregistre rien."""
    data = photo.file.read(MAX_PHOTO_BYTES + 1)
    if len(data) > MAX_PHOTO_BYTES:
        raise HTTPException(status.HTTP_413_CONTENT_TOO_LARGE, "Photo trop lourde (15 Mo max).")
    try:
        text = transcribe_photo(data)
    except InvalidImageError:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "Ce fichier n'est pas une photo lisible.")
    except GenerationError:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "La lecture de la photo a raté. Réessaie.")
    if not text:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "Aucun texte lisible. Reprends la photo plus près.")
    return Transcription(text=text)
