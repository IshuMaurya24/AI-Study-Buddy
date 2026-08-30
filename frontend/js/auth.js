/**
 * Handles the login and signup form submissions.
 * Expects to be loaded after api.js on login.html / signup.html.
 */

function showError(elementId, message) {
  const el = document.getElementById(elementId);
  el.textContent = message;
  el.classList.remove("hidden");
}

function hideError(elementId) {
  document.getElementById(elementId).classList.add("hidden");
}

function initLoginForm() {
  const form = document.getElementById("login-form");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    hideError("login-error");

    const username = document.getElementById("login-username").value.trim();
    const password = document.getElementById("login-password").value;
    const button = document.getElementById("login-submit");

    if (!username || !password) {
      showError("login-error", "Please fill in both fields.");
      return;
    }

    button.disabled = true;
    button.textContent = "Logging in...";
    try {
      await api.login(username, password);
      window.location.href = "index.html";
    } catch (err) {
      showError("login-error", err.message);
    } finally {
      button.disabled = false;
      button.textContent = "Log In";
    }
  });
}

function initSignupForm() {
  const form = document.getElementById("signup-form");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    hideError("signup-error");

    const username = document.getElementById("signup-username").value.trim();
    const email = document.getElementById("signup-email").value.trim();
    const password = document.getElementById("signup-password").value;
    const button = document.getElementById("signup-submit");

    if (!username || !email || !password) {
      showError("signup-error", "Please fill in all fields.");
      return;
    }
    if (password.length < 6) {
      showError("signup-error", "Password must be at least 6 characters.");
      return;
    }

    button.disabled = true;
    button.textContent = "Creating account...";
    try {
      await api.signup(username, email, password);
      await api.login(username, password);
      window.location.href = "index.html";
    } catch (err) {
      showError("signup-error", err.message);
    } finally {
      button.disabled = false;
      button.textContent = "Sign Up";
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  initLoginForm();
  initSignupForm();
});
