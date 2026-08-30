"""
Modular AI service responsible for talking to the configured LLM
provider and returning clean, validated JSON for quiz questions
and flashcards.

The provider is configurable via environment variables:
    AI_API_KEY   - your API key
    AI_MODEL     - model name (e.g. llama-3.3-70b-versatile)
    AI_API_URL   - completion endpoint
    AI_PROVIDER  - "groq" (default, free tier) or "anthropic"

Groq (https://console.groq.com) offers a free API tier with no credit
card required and is OpenAI-compatible, which is why it's the default
here. Anthropic's API is also supported if you set AI_PROVIDER=anthropic
and provide an Anthropic key/model instead.

This module never crashes the app: if the AI response cannot be
parsed as valid JSON, it retries once with a stricter prompt, and
if it still fails it raises AIServiceError which the routers turn
into a clean HTTP error.
"""
import os
import json
import re
import requests
from dotenv import load_dotenv

load_dotenv()

AI_PROVIDER = os.getenv("AI_PROVIDER", "groq").lower()
AI_API_KEY = os.getenv("AI_API_KEY", "")
AI_MODEL = os.getenv("AI_MODEL", "llama-3.3-70b-versatile")
AI_API_URL = os.getenv("AI_API_URL", "https://api.groq.com/openai/v1/chat/completions")


class AIServiceError(Exception):
    """Raised when the AI service fails to produce usable content."""
    pass


def _strip_code_fences(text: str) -> str:
    """AI models sometimes wrap JSON in ```json ... ``` even when told not to."""
    text = text.strip()
    text = re.sub(r"^```(json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    return text


def _call_ai(prompt: str) -> str:
    """
    Sends a single prompt to the configured AI provider and returns
    the raw text response. Raises AIServiceError on network/API failure.
    Supports Groq/OpenAI-style chat completions (default) and
    Anthropic's /v1/messages format.
    """
    if not AI_API_KEY:
        raise AIServiceError("AI_API_KEY is not configured on the server.")

    if AI_PROVIDER == "anthropic":
        headers = {
            "Content-Type": "application/json",
            "x-api-key": AI_API_KEY,
            "anthropic-version": "2023-06-01",
        }
        payload = {
            "model": AI_MODEL,
            "max_tokens": 2000,
            "messages": [{"role": "user", "content": prompt}],
        }
    else:
        # Groq and other OpenAI-compatible providers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {AI_API_KEY}",
        }
        payload = {
            "model": AI_MODEL,
            "max_tokens": 2000,
            "messages": [{"role": "user", "content": prompt}],
        }

    try:
        response = requests.post(AI_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
    except requests.RequestException as exc:
        # Surface the provider's error body when available - very useful
        # for diagnosing bad API keys or wrong model names.
        detail = ""
        try:
            detail = f" | {response.text[:300]}"
        except Exception:
            pass
        raise AIServiceError(f"AI request failed: {exc}{detail}")

    data = response.json()

    if AI_PROVIDER == "anthropic":
        try:
            parts = [block.get("text", "") for block in data.get("content", []) if block.get("type") == "text"]
            return "".join(parts)
        except (KeyError, AttributeError):
            raise AIServiceError("Unexpected response shape from AI provider.")
    else:
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            raise AIServiceError("Unexpected response shape from AI provider.")


def _build_quiz_prompt(topic: str, difficulty: str, count: int, strict: bool = False) -> str:
    strict_note = (
        "\n\nCRITICAL: Your previous response was not valid JSON. "
        "Respond with ONLY the JSON object. No markdown, no code fences, "
        "no commentary before or after."
        if strict else ""
    )
    return f"""You are an expert educational quiz generator.

Generate exactly {count} multiple-choice questions about:

Topic: {topic}
Difficulty: {difficulty}

Difficulty definitions:

Easy:
Basic definitions and introductory concepts.

Medium:
Conceptual understanding and application-based questions.

Hard:
Advanced concepts, problem solving, tricky scenarios, and deeper reasoning.

Each question must:

1. Be accurate.
2. Have exactly four options.
3. Have only one correct answer.
4. Have plausible incorrect options.
5. Include a short explanation.
6. Avoid duplicate questions.
7. Match the requested difficulty level.

Return ONLY valid JSON.

Required format:

{{
  "questions": [
    {{
      "question": "Question text",
      "options": {{
        "a": "Option A",
        "b": "Option B",
        "c": "Option C",
        "d": "Option D"
      }},
      "correct_option": "a",
      "explanation": "Short explanation"
    }}
  ]
}}

Do not include markdown.
Do not include ```json.
Do not include any text before or after the JSON.{strict_note}"""


def _build_flashcard_prompt(topic: str, difficulty: str, count: int, strict: bool = False) -> str:
    strict_note = (
        "\n\nCRITICAL: Your previous response was not valid JSON. "
        "Respond with ONLY the JSON object. No markdown, no code fences, "
        "no commentary before or after."
        if strict else ""
    )
    return f"""You are an expert educational flashcard generator.

Generate exactly {count} flashcards for:

Topic: {topic}
Difficulty: {difficulty}

Each flashcard must:

- Focus on one important concept.
- Have a short front side.
- Have a clear educational explanation on the back side.
- Avoid duplicate concepts.
- Match the requested difficulty.

Return ONLY valid JSON.

Format:

{{
  "flashcards": [
    {{
      "front": "Term or Question",
      "back": "Definition or Answer"
    }}
  ]
}}

Do not include markdown or any additional text.{strict_note}"""


def _validate_quiz_json(data: dict, expected_count: int) -> dict:
    if "questions" not in data or not isinstance(data["questions"], list):
        raise AIServiceError("AI response missing 'questions' list.")
    if len(data["questions"]) == 0:
        raise AIServiceError("AI returned zero questions.")

    for q in data["questions"]:
        if "question" not in q or "options" not in q or "correct_option" not in q:
            raise AIServiceError("AI question missing required fields.")
        options = q["options"]
        for key in ("a", "b", "c", "d"):
            if key not in options:
                raise AIServiceError("AI question missing one of the four options.")
        if q["correct_option"] not in ("a", "b", "c", "d"):
            raise AIServiceError("AI question has an invalid correct_option.")
    return data


def _validate_flashcard_json(data: dict) -> dict:
    if "flashcards" not in data or not isinstance(data["flashcards"], list):
        raise AIServiceError("AI response missing 'flashcards' list.")
    if len(data["flashcards"]) == 0:
        raise AIServiceError("AI returned zero flashcards.")
    for card in data["flashcards"]:
        if "front" not in card or "back" not in card:
            raise AIServiceError("AI flashcard missing 'front' or 'back'.")
    return data


def generate_quiz(topic: str, difficulty: str, count: int) -> dict:
    """
    Calls the AI provider to generate quiz questions.
    Retries once with a stricter prompt if the first response is invalid JSON.
    Raises AIServiceError if it still fails.
    """
    for attempt, strict in enumerate([False, True]):
        raw = _call_ai(_build_quiz_prompt(topic, difficulty, count, strict=strict))
        cleaned = _strip_code_fences(raw)
        try:
            data = json.loads(cleaned)
            return _validate_quiz_json(data, count)
        except (json.JSONDecodeError, AIServiceError):
            if attempt == 1:
                raise AIServiceError(
                    "The AI service returned an invalid response after two attempts. "
                    "Please try again."
                )
            continue


def generate_flashcards(topic: str, difficulty: str, count: int) -> dict:
    """
    Calls the AI provider to generate flashcards.
    Retries once with a stricter prompt if the first response is invalid JSON.
    """
    for attempt, strict in enumerate([False, True]):
        raw = _call_ai(_build_flashcard_prompt(topic, difficulty, count, strict=strict))
        cleaned = _strip_code_fences(raw)
        try:
            data = json.loads(cleaned)
            return _validate_flashcard_json(data)
        except (json.JSONDecodeError, AIServiceError):
            if attempt == 1:
                raise AIServiceError(
                    "The AI service returned an invalid response after two attempts. "
                    "Please try again."
                )
            continue
