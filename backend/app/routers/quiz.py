"""
Quiz generation and submission endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..dependencies import get_current_user
from ..services import ai_service

router = APIRouter(prefix="/api/quiz", tags=["quiz"])


def _get_or_create_topic(db: Session, name: str, user_id: int) -> models.Topic:
    topic = db.query(models.Topic).filter(models.Topic.name.ilike(name)).first()
    if topic:
        return topic
    topic = models.Topic(name=name, created_by=user_id)
    db.add(topic)
    db.commit()
    db.refresh(topic)
    return topic


@router.post("/generate", response_model=schemas.QuizGenerateResponse)
def generate_quiz(
    payload: schemas.QuizGenerateRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    try:
        ai_data = ai_service.generate_quiz(payload.topic, payload.difficulty, payload.count)
    except ai_service.AIServiceError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))

    topic = _get_or_create_topic(db, payload.topic, current_user.id)

    saved_questions = []
    for q in ai_data["questions"]:
        question = models.Question(
            topic_id=topic.id,
            question_text=q["question"],
            option_a=q["options"]["a"],
            option_b=q["options"]["b"],
            option_c=q["options"]["c"],
            option_d=q["options"]["d"],
            correct_option=q["correct_option"],
            explanation=q.get("explanation", ""),
            difficulty=payload.difficulty,
        )
        db.add(question)
        saved_questions.append(question)

    db.commit()
    for q in saved_questions:
        db.refresh(q)

    # IMPORTANT: never send correct_option or explanation to the frontend here
    response_questions = [
        schemas.QuizQuestionOut(
            id=q.id,
            question=q.question_text,
            options=schemas.QuizOptionOut(
                a=q.option_a, b=q.option_b, c=q.option_c, d=q.option_d
            ),
        )
        for q in saved_questions
    ]

    return schemas.QuizGenerateResponse(
        topic=topic.name,
        difficulty=payload.difficulty,
        questions=response_questions,
    )


@router.post("/submit", response_model=schemas.QuizSubmitResponse)
def submit_quiz(
    payload: schemas.QuizSubmitRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if not payload.question_ids:
        raise HTTPException(status_code=400, detail="No questions submitted.")

    questions = db.query(models.Question).filter(
        models.Question.id.in_(payload.question_ids)
    ).all()
    if not questions:
        raise HTTPException(status_code=404, detail="Submitted questions were not found.")

    questions_by_id = {q.id: q for q in questions}
    topic_id = questions[0].topic_id
    difficulty = questions[0].difficulty

    correct_count = 0
    results = []
    for qid in payload.question_ids:
        question = questions_by_id.get(qid)
        if not question:
            continue
        selected = payload.answers.get(str(qid))
        is_correct = selected == question.correct_option
        if is_correct:
            correct_count += 1
        results.append(
            schemas.QuestionResult(
                question_id=qid,
                selected_option=selected,
                correct_option=question.correct_option,
                is_correct=is_correct,
                explanation=question.explanation,
            )
        )

    total = len(payload.question_ids)
    percentage = round((correct_count / total) * 100, 2) if total else 0.0

    attempt = models.QuizAttempt(
        user_id=current_user.id,
        topic_id=topic_id,
        difficulty=difficulty,
        total_questions=total,
        correct_answers=correct_count,
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    for result in results:
        db.add(models.AttemptAnswer(
            attempt_id=attempt.id,
            question_id=result.question_id,
            selected_option=result.selected_option,
            is_correct=result.is_correct,
        ))
    db.commit()

    return schemas.QuizSubmitResponse(
        attempt_id=attempt.id,
        score=correct_count,
        total_questions=total,
        percentage=percentage,
        results=results,
    )
