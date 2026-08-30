-- AI Study Buddy - PostgreSQL schema
-- Run this against a fresh database, e.g.:
--   createdb ai_study_buddy
--   psql -d ai_study_buddy -f schema.sql
-- (Note: SQLAlchemy will also auto-create these tables on backend startup,
-- so running this file manually is optional but useful for inspection.)

-- Users
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Topics
CREATE TABLE IF NOT EXISTS topics (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Questions
CREATE TABLE IF NOT EXISTS questions (
    id SERIAL PRIMARY KEY,
    topic_id INTEGER REFERENCES topics(id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    correct_option CHAR(1) NOT NULL CHECK (
        correct_option IN ('a', 'b', 'c', 'd')
    ),
    explanation TEXT,
    difficulty VARCHAR(10) NOT NULL CHECK (
        difficulty IN ('easy', 'medium', 'hard')
    ),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Flashcards
CREATE TABLE IF NOT EXISTS flashcards (
    id SERIAL PRIMARY KEY,
    topic_id INTEGER REFERENCES topics(id) ON DELETE CASCADE,
    front_text TEXT NOT NULL,
    back_text TEXT NOT NULL,
    difficulty VARCHAR(10) CHECK (
        difficulty IN ('easy', 'medium', 'hard')
    ),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Quiz Attempts
CREATE TABLE IF NOT EXISTS quiz_attempts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    topic_id INTEGER REFERENCES topics(id),
    difficulty VARCHAR(10) CHECK (
        difficulty IN ('easy', 'medium', 'hard')
    ),
    total_questions INTEGER NOT NULL,
    correct_answers INTEGER NOT NULL,
    taken_at TIMESTAMP DEFAULT NOW()
);

-- Attempt Answers
CREATE TABLE IF NOT EXISTS attempt_answers (
    id SERIAL PRIMARY KEY,
    attempt_id INTEGER REFERENCES quiz_attempts(id) ON DELETE CASCADE,
    question_id INTEGER REFERENCES questions(id),
    selected_option CHAR(1) CHECK (
        selected_option IN ('a', 'b', 'c', 'd')
    ),
    is_correct BOOLEAN NOT NULL
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_questions_topic ON questions(topic_id);
CREATE INDEX IF NOT EXISTS idx_attempts_user ON quiz_attempts(user_id);
CREATE INDEX IF NOT EXISTS idx_attempts_user_taken_at
ON quiz_attempts(user_id, taken_at DESC);
CREATE INDEX IF NOT EXISTS idx_attempt_answers_attempt
ON attempt_answers(attempt_id);
