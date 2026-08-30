"""
Quiz history and weak-topic analysis endpoints.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, Integer

from .. import models, schemas
from ..database import get_db
from ..dependencies import get_current_user

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("", response_model=list[schemas.HistoryItem])
def get_history(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    attempts = (
        db.query(models.QuizAttempt)
        .filter(models.QuizAttempt.user_id == current_user.id)
        .order_by(models.QuizAttempt.taken_at.desc())
        .all()
    )

    results = []
    for attempt in attempts:
        percentage = (
            round((attempt.correct_answers / attempt.total_questions) * 100, 2)
            if attempt.total_questions else 0.0
        )
        results.append(schemas.HistoryItem(
            attempt_id=attempt.id,
            topic=attempt.topic.name if attempt.topic else "Unknown",
            difficulty=attempt.difficulty or "unknown",
            score=attempt.correct_answers,
            total_questions=attempt.total_questions,
            percentage=percentage,
            taken_at=attempt.taken_at,
        ))
    return results


@router.get("/weak-topics", response_model=list[schemas.WeakTopicItem])
def get_weak_topics(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Analyzes attempt_answers joined through quiz_attempts -> questions -> topics
    to find topics where the current user has the lowest accuracy.
    """
    rows = (
        db.query(
            models.Topic.name.label("topic_name"),
            func.count(models.AttemptAnswer.id).label("total_attempted"),
            func.sum(
                func.cast(models.AttemptAnswer.is_correct, Integer)
            ).label("correct"),
        )
        .join(models.QuizAttempt, models.QuizAttempt.id == models.AttemptAnswer.attempt_id)
        .join(models.Topic, models.Topic.id == models.QuizAttempt.topic_id)
        .filter(models.QuizAttempt.user_id == current_user.id)
        .group_by(models.Topic.name)
        .all()
    )

    weak_topics = []
    for row in rows:
        total = row.total_attempted or 0
        correct = row.correct or 0
        accuracy = round((correct / total) * 100, 2) if total else 0.0
        weak_topics.append(schemas.WeakTopicItem(
            topic=row.topic_name,
            total_attempted=total,
            correct=correct,
            accuracy=accuracy,
        ))

    weak_topics.sort(key=lambda t: t.accuracy)
    return weak_topics
