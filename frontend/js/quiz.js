/**
 * Quiz setup + quiz-taking logic for quiz.html.
 * Flow: fill setup form -> generate quiz -> answer one question
 * at a time -> submit -> redirect to results.html.
 */

let selectedDifficulty = "medium";
let selectedCount = 5;

let quizState = {
  topic: "",
  difficulty: "",
  questions: [],     // [{id, question, options}]
  currentIndex: 0,
  questionIds: [],
  answers: {},        // { questionId: selectedOption }
  answeredCurrent: false,
};

function initChoiceGroups() {
  document.querySelectorAll("#difficulty-choices .choice").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll("#difficulty-choices .choice").forEach((b) => b.classList.remove("selected"));
      btn.classList.add("selected");
      selectedDifficulty = btn.dataset.value;
    });
  });

  document.querySelectorAll("#count-choices .choice").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll("#count-choices .choice").forEach((b) => b.classList.remove("selected"));
      btn.classList.add("selected");
      selectedCount = parseInt(btn.dataset.value, 10);
    });
  });
}

function initSetupForm() {
  const form = document.getElementById("quiz-setup-form");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const topic = document.getElementById("quiz-topic").value.trim();
    const errorBox = document.getElementById("setup-error");
    errorBox.classList.add("hidden");

    if (!topic) {
      errorBox.textContent = "Please enter a topic.";
      errorBox.classList.remove("hidden");
      return;
    }

    document.getElementById("setup-card").classList.add("hidden");
    document.getElementById("loading-card").classList.remove("hidden");

    try {
      const data = await api.generateQuiz(topic, selectedDifficulty, selectedCount);
      quizState = {
        topic: data.topic,
        difficulty: data.difficulty,
        questions: data.questions,
        currentIndex: 0,
        questionIds: data.questions.map((q) => q.id),
        answers: {},
        answeredCurrent: false,
      };
      document.getElementById("loading-card").classList.add("hidden");
      document.getElementById("quiz-card").classList.remove("hidden");
      renderQuestion();
    } catch (err) {
      document.getElementById("loading-card").classList.add("hidden");
      document.getElementById("setup-card").classList.remove("hidden");
      errorBox.textContent = err.message;
      errorBox.classList.remove("hidden");
    }
  });
}

function renderQuestion() {
  const q = quizState.questions[quizState.currentIndex];
  const total = quizState.questions.length;

  document.getElementById("progress-text").textContent =
    `Question ${quizState.currentIndex + 1} of ${total} — ${quizState.topic}`;
  document.getElementById("progress-bar-fill").style.width =
    `${((quizState.currentIndex) / total) * 100}%`;
  document.getElementById("question-text").textContent = q.question;

  const optionsWrap = document.getElementById("options-wrap");
  optionsWrap.innerHTML = "";
  quizState.answeredCurrent = false;
  document.getElementById("next-btn").classList.add("hidden");
  document.getElementById("explanation-box").classList.add("hidden");

  ["a", "b", "c", "d"].forEach((key) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "option";
    btn.textContent = `${key.toUpperCase()}. ${q.options[key]}`;
    btn.dataset.key = key;
    btn.addEventListener("click", () => selectAnswer(q.id, key));
    optionsWrap.appendChild(btn);
  });
}

async function selectAnswer(questionId, selectedKey) {
  if (quizState.answeredCurrent) return;
  quizState.answeredCurrent = true;
  quizState.answers[questionId] = selectedKey;

  // Disable all options immediately (no correct answer shown until submission,
  // but we mark the user's own choice as selected for clarity).
  document.querySelectorAll("#options-wrap .option").forEach((btn) => {
    btn.disabled = true;
    if (btn.dataset.key === selectedKey) {
      btn.style.borderColor = "var(--color-primary)";
      btn.style.background = "var(--color-primary-light)";
    }
  });

  document.getElementById("next-btn").classList.remove("hidden");
  const isLast = quizState.currentIndex === quizState.questions.length - 1;
  document.getElementById("next-btn").textContent = isLast ? "Finish Quiz" : "Next Question";
}

function initNextButton() {
  const btn = document.getElementById("next-btn");
  if (!btn) return;

  btn.addEventListener("click", async () => {
    const isLast = quizState.currentIndex === quizState.questions.length - 1;
    if (!isLast) {
      quizState.currentIndex += 1;
      renderQuestion();
      return;
    }

    // Submit the quiz
    btn.disabled = true;
    btn.textContent = "Submitting...";
    try {
      const result = await api.submitQuiz(quizState.questionIds, quizState.answers);
      sessionStorage.setItem("asb_last_result", JSON.stringify({
        ...result,
        topic: quizState.topic,
        difficulty: quizState.difficulty,
      }));
      window.location.href = "results.html";
    } catch (err) {
      alert("Could not submit quiz: " + err.message);
      btn.disabled = false;
      btn.textContent = "Finish Quiz";
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  if (typeof api !== "undefined") api.requireAuth();
  initChoiceGroups();
  initSetupForm();
  initNextButton();
});
