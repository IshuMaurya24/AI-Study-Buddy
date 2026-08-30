"""
SQLAlchemy ORM models matching database/schema.sql exactly.
"""
from sqlalchemy import (
    Column, Integer, String, Text, TIMESTAMP, ForeignKey, CheckConstraint, Boolean, func
)
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    topics = relationship("Topic", back_populates="creator")
    quiz_attempts = relationship("QuizAttempt", back_populates="user")


class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(TIMESTAMP, server_default=func.now())

    creator = relationship("User", back_populates="topics")
    questions = relationship("Question", back_populates="topic", cascade="all, delete-orphan")
    flashcards = relationship("Flashcard", back_populates="topic", cascade="all, delete-orphan")


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="CASCADE"), index=True)
    question_text = Column(Text, nullable=False)
    option_a = Column(Text, nullable=False)
    option_b = Column(Text, nullable=False)
    option_c = Column(Text, nullable=False)
    option_d = Column(Text, nullable=False)
    correct_option = Column(String(1), nullable=False)
    explanation = Column(Text)
    difficulty = Column(String(10), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    __table_args__ = (
        CheckConstraint("correct_option IN ('a','b','c','d')", name="ck_correct_option"),
        CheckConstraint("difficulty IN ('easy','medium','hard')", name="ck_question_difficulty"),
    )

    topic = relationship("Topic", back_populates="questions")


class Flashcard(Base):
    __tablename__ = "flashcards"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="CASCADE"), index=True)
    front_text = Column(Text, nullable=False)
    back_text = Column(Text, nullable=False)
    difficulty = Column(String(10))
    created_at = Column(TIMESTAMP, server_default=func.now())

    __table_args__ = (
        CheckConstraint("difficulty IN ('easy','medium','hard')", name="ck_flashcard_difficulty"),
    )

    topic = relationship("Topic", back_populates="flashcards")


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"))
    difficulty = Column(String(10))
    total_questions = Column(Integer, nullable=False)
    correct_answers = Column(Integer, nullable=False)
    taken_at = Column(TIMESTAMP, server_default=func.now())

    __table_args__ = (
        CheckConstraint("difficulty IN ('easy','medium','hard')", name="ck_attempt_difficulty"),
    )

    user = relationship("User", back_populates="quiz_attempts")
    topic = relationship("Topic")
    answers = relationship("AttemptAnswer", back_populates="attempt", cascade="all, delete-orphan")


class AttemptAnswer(Base):
    __tablename__ = "attempt_answers"

    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("quiz_attempts.id", ondelete="CASCADE"), index=True)
    question_id = Column(Integer, ForeignKey("questions.id"))
    selected_option = Column(String(1))
    is_correct = Column(Boolean, nullable=False)

    __table_args__ = (
        CheckConstraint("selected_option IN ('a','b','c','d')", name="ck_selected_option"),
    )

    attempt = relationship("QuizAttempt", back_populates="answers")
    question = relationship("Question")
