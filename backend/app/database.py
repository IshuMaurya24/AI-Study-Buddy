"""
Database connection setup using SQLAlchemy.
Reads DATABASE_URL from environment variables (.env file).
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://username:password@localhost:5432/ai_study_buddy",
)

# echo=False keeps logs clean; set True while debugging SQL
engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    FastAPI dependency that yields a DB session and
    always closes it after the request finishes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
