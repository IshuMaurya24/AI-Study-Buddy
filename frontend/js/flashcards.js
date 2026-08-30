/**
 * Flashcard generation + flip/navigation logic for flashcards.html.
 */

let fcSelectedDifficulty = "easy";
let fcSelectedCount = 10;
let fcState = { topic: "", cards: [], index: 0 };

function initFcChoiceGroups() {
  document.querySelectorAll("#fc-difficulty-choices .choice").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll("#fc-difficulty-choices .choice").forEach((b) => b.classList.remove("selected"));
      btn.classList.add("selected");
      fcSelectedDifficulty = btn.dataset.value;
    });
  });

  document.querySelectorAll("#fc-count-choices .choice").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll("#fc-count-choices .choice").forEach((b) => b.classList.remove("selected"));
      btn.classList.add("selected");
      fcSelectedCount = parseInt(btn.dataset.value, 10);
    });
  });
}

function initFcSetupForm() {
  const form = document.getElementById("fc-setup-form");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const topic = document.getElementById("fc-topic").value.trim();
    const errorBox = document.getElementById("fc-setup-error");
    errorBox.classList.add("hidden");

    if (!topic) {
      errorBox.textContent = "Please enter a topic.";
      errorBox.classList.remove("hidden");
      return;
    }

    document.getElementById("fc-setup-card").classList.add("hidden");
    document.getElementById("fc-loading-card").classList.remove("hidden");

    try {
      const data = await api.generateFlashcards(topic, fcSelectedDifficulty, fcSelectedCount);
      fcState = { topic: data.topic, cards: data.flashcards, index: 0 };
      document.getElementById("fc-loading-card").classList.add("hidden");
      document.getElementById("fc-study-card").classList.remove("hidden");
      renderFlashcard();
    } catch (err) {
      document.getElementById("fc-loading-card").classList.add("hidden");
      document.getElementById("fc-setup-card").classList.remove("hidden");
      errorBox.textContent = err.message;
      errorBox.classList.remove("hidden");
    }
  });
}

function renderFlashcard() {
  const card = fcState.cards[fcState.index];
  document.getElementById("fc-front-text").textContent = card.front;
  document.getElementById("fc-back-text").textContent = card.back;
  document.getElementById("fc-progress").textContent =
    `Card ${fcState.index + 1} of ${fcState.cards.length} — ${fcState.topic}`;
  document.getElementById("flashcard").classList.remove("flipped");

  document.getElementById("fc-prev-btn").disabled = fcState.index === 0;
  document.getElementById("fc-next-btn").disabled = fcState.index === fcState.cards.length - 1;
}

function initFlashcardControls() {
  const flashcardEl = document.getElementById("flashcard");
  if (!flashcardEl) return;

  flashcardEl.addEventListener("click", () => flashcardEl.classList.toggle("flipped"));

  document.getElementById("fc-prev-btn").addEventListener("click", () => {
    if (fcState.index > 0) {
      fcState.index -= 1;
      renderFlashcard();
    }
  });

  document.getElementById("fc-next-btn").addEventListener("click", () => {
    if (fcState.index < fcState.cards.length - 1) {
      fcState.index += 1;
      renderFlashcard();
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  if (typeof api !== "undefined") api.requireAuth();
  initFcChoiceGroups();
  initFcSetupForm();
  initFlashcardControls();
});
