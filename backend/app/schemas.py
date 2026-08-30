"""
Pydantic schemas for request/response validation.
"""
from datetime import datetime
from typing import Optional, Dict, List
from pydantic import BaseModel, EmailStr, field_validator


# ---------- Auth ----------

class UserSignup(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator("username")
    @classmethod
    def username_valid(cls, v):
        v = v.strip()
        if len(v) < 3 or len(v) > 50:
            raise ValueError("Username must be between 3 and 50 characters")
        if not v.replace("_", "").isalnum():
            raise ValueError("Username can only contain letters, numbers, and underscores")
        return v

    @field_validator("password")
    @classmethod
    def password_valid(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters long")
        return v


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True


# ---------- Quiz generation ----------

class QuizGenerateRequest(BaseModel):
    topic: str
    difficulty: str
    count: int = 5

    @field_validator("topic")
    @classmethod
    def topic_not_empty(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("Topic cannot be empty")
        if len(v) > 150:
            raise ValueError("Topic must be under 150 characters")
        return v

    @field_validator("difficulty")
    @classmethod
    def difficulty_valid(cls, v):
        v = v.lower().strip()
        if v not in ("easy", "medium", "hard"):
            raise ValueError("Difficulty must be easy, medium, or hard")
        return v

    @field_validator("count")
    @classmethod
    def count_valid(cls, v):
        if v < 1 or v > 25:
            raise ValueError("Question count must be between 1 and 25")
        return v


class QuizOptionOut(BaseModel):
    a: str
    b: str
    c: str
    d: str


class QuizQuestionOut(BaseModel):
    id: int
    question: str
    options: QuizOptionOut


class QuizGenerateResponse(BaseModel):
    topic: str
    difficulty: str
    questions: List[QuizQuestionOut]


# ---------- Quiz submission ----------

class QuizSubmitRequest(BaseModel):
    question_ids: List[int]
    answers: Dict[str, str]


class QuestionResult(BaseModel):
    question_id: int
    selected_option: Optional[str]
    correct_option: str
    is_correct: bool
    explanation: Optional[str]


class QuizSubmitResponse(BaseModel):
    attempt_id: int
    score: int
    total_questions: int
    percentage: float
    results: List[QuestionResult]


# ---------- Flashcards ----------

class FlashcardGenerateRequest(BaseModel):
    topic: str
    difficulty: str = "medium"
    count: int = 10

    @field_validator("topic")
    @classmethod
    def topic_not_empty(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("Topic cannot be empty")
        return v

    @field_validator("difficulty")
    @classmethod
    def difficulty_valid(cls, v):
        v = v.lower().strip()
        if v not in ("easy", "medium", "hard"):
            raise ValueError("Difficulty must be easy, medium, or hard")
        return v

    @field_validator("count")
    @classmethod
    def count_valid(cls, v):
        if v < 1 or v > 30:
            raise ValueError("Flashcard count must be between 1 and 30")
        return v


class FlashcardOut(BaseModel):
    id: int
    front: str
    back: str


class FlashcardGenerateResponse(BaseModel):
    topic: str
    flashcards: List[FlashcardOut]


# ---------- History ----------

class HistoryItem(BaseModel):
    attempt_id: int
    topic: str
    difficulty: str
    score: int
    total_questions: int
    percentage: float
    taken_at: datetime


class WeakTopicItem(BaseModel):
    topic: str
    total_attempted: int
    correct: int
    accuracy: float
