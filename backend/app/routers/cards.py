from fastapi import APIRouter, HTTPException, status

from app.auth import CurrentUser, SessionDep
from app.models import Card, User
from app.schemas import CardRead, CardUpdate

router = APIRouter(prefix="/cards", tags=["cards"])

VRAI_FAUX = ("Vrai", "Faux")


def get_owned_card(session: SessionDep, card_id: int, user: User) -> Card:
    card = session.get(Card, card_id)
    if card is None or card.lesson.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Carte introuvable")
    return card


def check_card(card: Card) -> None:
    """Règles de forme par type, pour qu'une carte corrigée à la main reste jouable."""
    if card.type == "qcm":
        if len(card.choices) != 4 or card.answer not in card.choices:
            raise HTTPException(422, "Un QCM a 4 choix, dont la bonne réponse.")
    elif card.choices:
        raise HTTPException(422, "Seul un QCM a des choix.")
    if card.type == "vrai_faux" and card.answer not in VRAI_FAUX:
        raise HTTPException(422, "La réponse doit être « Vrai » ou « Faux ».")


@router.patch("/{card_id}")
def update_card(card_id: int, body: CardUpdate, session: SessionDep, user: CurrentUser) -> CardRead:
    card = get_owned_card(session, card_id, user)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(card, field, value)
    check_card(card)
    session.add(card)
    session.commit()
    session.refresh(card)
    return CardRead.model_validate(card, from_attributes=True)


@router.delete("/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_card(card_id: int, session: SessionDep, user: CurrentUser) -> None:
    session.delete(get_owned_card(session, card_id, user))
    session.commit()
