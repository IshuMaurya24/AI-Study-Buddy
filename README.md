# AI Study Buddy – Quiz & Flashcard Generator

An AI-powered study web app: enter any topic, get instant multiple-choice
quizzes and flashcards, and track your progress (including weak topics)
over time.

Built for a university project / portfolio piece, using a clean, beginner-friendly
FastAPI + PostgreSQL backend and a vanilla HTML/CSS/JS frontend.

---

## Features

- Signup / login with JWT authentication (bcrypt-hashed passwords)
- AI-generated multiple-choice quizzes (topic, difficulty, question count)
- One-question-at-a-time quiz flow, with the correct answer never sent to
  the browser until you submit
- Instant scoring + per-question explanations after submission
- AI-generated flashcards with a flip animation
- Quiz history dashboard
- Weak-topic analysis (lowest accuracy topics, based on your real attempts)
- Clean, responsive, mobile-friendly UI with loading/empty/error states

---

## Technology Stack

**Backend:** Python, FastAPI, SQLAlchemy, PostgreSQL, Pydantic, JWT (python-jose),
bcrypt, Uvicorn, python-dotenv

**Frontend:** HTML5, CSS3, vanilla JavaScript (Fetch API) — no frameworks

**AI:** Configurable via environment variables — works out of the box with
Anthropic's Messages API, but any provider with a similar `/v1/messages`-style
JSON response can be swapped in by changing `AI_API_URL`.

---

## Project Structure

```text
ai-study-buddy/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app, CORS, routers, error handlers
│   │   ├── database.py        # SQLAlchemy engine/session setup
│   │   ├── models.py          # ORM models (matches database/schema.sql)
│   │   ├── schemas.py         # Pydantic request/response schemas
│   │   ├── auth.py            # Password hashing + JWT helpers
│   │   ├── dependencies.py    # get_current_user() auth dependency
│   │   ├── routers/
│   │   │   ├── auth.py        # /api/auth/signup, /api/auth/login
│   │   │   ├── quiz.py        # /api/quiz/generate, /api/quiz/submit
│   │   │   ├── flashcards.py  # /api/flashcards/generate
│   │   │   └── history.py     # /api/history, /api/history/weak-topics
│   │   └── services/
│   │       └── ai_service.py  # AI prompt building, calling, JSON validation, retry
│   ├── requirements.txt
│   ├── .env.example
│   └── run.py
├── frontend/
│   ├── index.html, login.html, signup.html
│   ├── quiz.html, results.html, flashcards.html, history.html
│   ├── css/style.css
│   └── js/api.js, auth.js, quiz.js, flashcards.js, history.js
├── database/
│   └── schema.sql             # Raw SQL schema (SQLAlchemy also auto-creates it)
└── README.md
```

---

## Database Schema

See `database/schema.sql`. Tables: `users`, `topics`, `questions`,
`flashcards`, `quiz_attempts`, `attempt_answers`, with indexes on the
common lookup paths (questions by topic, attempts by user/date, etc.).

You don't have to run this file manually — `Base.metadata.create_all()`
in `main.py` creates all tables automatically the first time the backend
starts, as long as `DATABASE_URL` points at a valid, existing database.

---

## Setup Instructions

### 1. PostgreSQL setup

Install PostgreSQL, then create a database:

```bash
createdb ai_study_buddy
```

(or via `psql`: `CREATE DATABASE ai_study_buddy;`)

### 2. Backend setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# then edit .env:
#   DATABASE_URL=postgresql://<user>:<password>@localhost:5432/ai_study_buddy
#   JWT_SECRET_KEY=<any long random string>
#   AI_API_KEY=<your Anthropic (or other provider) API key>
#   AI_MODEL=claude-sonnet-4-6
```

Run the backend:

```bash
python run.py
```

This starts the API at `http://localhost:8000` and prints interactive
docs at `http://localhost:8000/docs`. Tables are created automatically
on first startup.

### 3. Frontend setup

The frontend is plain static HTML/CSS/JS — no build step. From the
`frontend/` folder, just serve it with any static server, e.g.:

```bash
cd frontend
python3 -m http.server 5500
```

Then open `http://localhost:5500/login.html` in your browser.

(`js/api.js` points at `http://localhost:8000` by default — change
`API_BASE_URL` at the top of that file if your backend runs elsewhere.)

### 4. Try it out

1. Sign up for an account.
2. Go to **Generate Quiz**, enter a topic (e.g. "Database Management System"),
   pick a difficulty and question count, and generate.
3. Answer the questions one at a time, then submit to see your score,
   percentage, and per-question explanations.
4. Try **Generate Flashcards** for the same or a different topic.
5. Check **History** to see past attempts and your weakest topics.

---

## API Endpoints

| Method | Endpoint                     | Auth | Description                          |
|--------|-------------------------------|------|---------------------------------------|
| POST   | `/api/auth/signup`            | No   | Create an account                     |
| POST   | `/api/auth/login`             | No   | Log in, returns a JWT                 |
| POST   | `/api/quiz/generate`          | Yes  | Generate an AI quiz for a topic       |
| POST   | `/api/quiz/submit`            | Yes  | Submit answers, get score + review    |
| POST   | `/api/flashcards/generate`    | Yes  | Generate AI flashcards for a topic    |
| GET    | `/api/history`                | Yes  | List the user's past quiz attempts    |
| GET    | `/api/history/weak-topics`    | Yes  | Topics sorted by lowest accuracy      |

Full interactive documentation (with request/response schemas) is available
at `/docs` once the backend is running.

---

## Design Notes

- **Answers stay server-side.** `/api/quiz/generate` never sends
  `correct_option` or `explanation` to the browser — those only come
  back after `/api/quiz/submit`, so there's no way to inspect the
  frontend's network tab to cheat.
- **AI JSON is validated and retried.** `ai_service.py` strips stray
  code fences, parses JSON, and validates the shape (four options, a
  valid `correct_option`, etc.). If the first response is malformed,
  it retries once with a stricter prompt before giving up with a clean
  502 error — the app never crashes on a bad AI response.
- **Passwords** are hashed with bcrypt (never stored in plain text).

---

## Future Improvements

- Personalized AI study plans based on weak-topic history
- Spaced-repetition scheduling for flashcards
- Question bookmarking
- Admin dashboard / analytics
- Support for multiple AI providers via a pluggable adapter layer

---

## Screenshots

_Add screenshots here after running the app locally, e.g._

- `docs/screenshot-quiz.png`
- `docs/screenshot-flashcards.png`
- `docs/screenshot-history.png`
