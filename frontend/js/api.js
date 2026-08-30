/**
 * Centralized API module for the AI Study Buddy frontend.
 * All network calls go through here so error handling stays in one place.
 */

const API_BASE_URL = "http://localhost:8000";

/** Reads the stored JWT, if any. */
function getToken() {
  return localStorage.getItem("asb_token");
}

function setToken(token) {
  localStorage.setItem("asb_token", token);
}

function clearToken() {
  localStorage.removeItem("asb_token");
}

function isLoggedIn() {
  return !!getToken();
}

/**
 * Core request helper. Handles JSON encoding/decoding, auth headers,
 * and turns non-2xx responses into thrown Error objects with a
 * readable message so calling code can just try/catch.
 */
async function request(path, { method = "GET", body = null, auth = false } = {}) {
  const headers = { "Content-Type": "application/json" };

  if (auth) {
    const token = getToken();
    if (!token) {
      throw new Error("You must be logged in to do that.");
    }
    headers["Authorization"] = `Bearer ${token}`;
  }

  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch (networkError) {
    throw new Error("Network error - is the backend server running?");
  }

  let data = null;
  try {
    data = await response.json();
  } catch (_) {
    // Some responses (e.g. 204) may have no body.
  }

  if (!response.ok) {
    if (response.status === 401) {
      clearToken();
      throw new Error((data && data.detail) || "Session expired. Please log in again.");
    }
    const detail = data && data.detail ? data.detail : `Request failed (${response.status})`;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }

  return data;
}

/* ---------- Auth ---------- */

async function signup(username, email, password) {
  return request("/api/auth/signup", {
    method: "POST",
    body: { username, email, password },
  });
}

async function login(username, password) {
  const data = await request("/api/auth/login", {
    method: "POST",
    body: { username, password },
  });
  setToken(data.access_token);
  return data;
}

function logout() {
  clearToken();
  window.location.href = "login.html";
}

/* ---------- Quiz ---------- */

async function generateQuiz(topic, difficulty, count) {
  return request("/api/quiz/generate", {
    method: "POST",
    auth: true,
    body: { topic, difficulty, count },
  });
}

async function submitQuiz(questionIds, answers) {
  return request("/api/quiz/submit", {
    method: "POST",
    auth: true,
    body: { question_ids: questionIds, answers },
  });
}

/* ---------- Flashcards ---------- */

async function generateFlashcards(topic, difficulty, count) {
  return request("/api/flashcards/generate", {
    method: "POST",
    auth: true,
    body: { topic, difficulty, count },
  });
}

/* ---------- History ---------- */

async function getHistory() {
  return request("/api/history", { auth: true });
}

async function getWeakTopics() {
  return request("/api/history/weak-topics", { auth: true });
}

/** Guards pages that require login; redirects to login.html otherwise. */
function requireAuth() {
  if (!isLoggedIn()) {
    window.location.href = "login.html";
  }
}

const api = {
  signup,
  login,
  logout,
  isLoggedIn,
  requireAuth,
  generateQuiz,
  submitQuiz,
  generateFlashcards,
  getHistory,
  getWeakTopics,
};
