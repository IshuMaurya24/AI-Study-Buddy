"""
FastAPI application entry point.
Wires up CORS, database table creation, and all routers.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from .database import Base, engine
from .routers import auth, quiz, flashcards, history

# Create tables if they don't already exist (safe to run every startup).
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Study Buddy API",
    description="Backend for the AI-powered Quiz & Flashcard Generator",
    version="1.0.0",
)

# Allow the vanilla-JS frontend (served from any local origin) to call the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(quiz.router)
app.include_router(flashcards.router)
app.include_router(history.router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Turns Pydantic validation errors into a clean, predictable JSON shape."""
    return JSONResponse(
        status_code=422,
        content={"detail": "Invalid input.", "errors": exc.errors()},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.get("/")
def root():
    return {"message": "AI Study Buddy API is running.", "docs": "/docs"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
