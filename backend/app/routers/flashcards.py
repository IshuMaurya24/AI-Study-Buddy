"""
Flashcard generation endpoint.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..dependencies import get_current_user
from ..services import ai_service
from .quiz import _get_or_create_topic

router = APIRouter(prefix="/api/flashcards", tags=["flashcards"])


@router.post("/generate", response_model=schemas.FlashcardGenerateResponse)
def generate_flashcards(
    payload: schemas.FlashcardGenerateRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    try:
        ai_data = ai_service.generate_flashcards(payload.topic, payload.difficulty, payload.count)
    except ai_service.AIServiceError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))

    topic = _get_or_create_topic(db, payload.topic, current_user.id)

    saved_cards = []
    for card in ai_data["flashcards"]:
        flashcard = models.Flashcard(
            topic_id=topic.id,
            front_text=card["front"],
            back_text=card["back"],
            difficulty=payload.difficulty,
        )
        db.add(flashcard)
        saved_cards.append(flashcard)

    db.commit()
    for c in saved_cards:
        db.refresh(c)

    return schemas.FlashcardGenerateResponse(
        topic=topic.name,
        flashcards=[
            schemas.FlashcardOut(id=c.id, front=c.front_text, back=c.back_text)
            for c in saved_cards
        ],
    )
