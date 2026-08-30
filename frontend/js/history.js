/**
 * Renders quiz history and weak-topic analysis on history.html.
 */

function difficultyBadge(difficulty) {
  const cls = { easy: "badge-easy", medium: "badge-medium", hard: "badge-hard" }[difficulty] || "badge-medium";
  return `<span class="badge ${cls}">${difficulty}</span>`;
}

function formatDate(isoString) {
  const d = new Date(isoString);
  return d.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" }) +
    " " + d.toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" });
}

async function loadHistory() {
  const tableWrap = document.getElementById("history-table-wrap");
  const emptyState = document.getElementById("history-empty");
  const loading = document.getElementById("history-loading");

  try {
    const attempts = await api.getHistory();
    loading.classList.add("hidden");

    if (!attempts.length) {
      emptyState.classList.remove("hidden");
      return;
    }

    const rows = attempts.map((a) => `
      <tr>
        <td>${a.topic}</td>
        <td>${difficultyBadge(a.difficulty)}</td>
        <td>${a.score} / ${a.total_questions}</td>
        <td>${a.percentage}%</td>
        <td>${formatDate(a.taken_at)}</td>
      </tr>
    `).join("");

    tableWrap.innerHTML = `
      <table>
        <thead>
          <tr><th>Topic</th><th>Difficulty</th><th>Score</th><th>Percentage</th><th>Date</th></tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>
    `;
    tableWrap.classList.remove("hidden");
  } catch (err) {
    loading.classList.add("hidden");
    tableWrap.innerHTML = `<div class="alert alert-error">Could not load history: ${err.message}</div>`;
    tableWrap.classList.remove("hidden");
  }
}

async function loadWeakTopics() {
  const wrap = document.getElementById("weak-topics-wrap");
  const emptyState = document.getElementById("weak-topics-empty");
  const loading = document.getElementById("weak-topics-loading");

  try {
    const topics = await api.getWeakTopics();
    loading.classList.add("hidden");

    if (!topics.length) {
      emptyState.classList.remove("hidden");
      return;
    }

    wrap.innerHTML = topics.map((t, i) => `
      <div class="weak-topic-row">
        <span>${i + 1}. ${t.topic}</span>
        <strong>${t.accuracy}%</strong>
      </div>
    `).join("");
    wrap.classList.remove("hidden");
  } catch (err) {
    loading.classList.add("hidden");
    wrap.innerHTML = `<div class="alert alert-error">Could not load weak topics: ${err.message}</div>`;
    wrap.classList.remove("hidden");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  if (typeof api !== "undefined") api.requireAuth();
  loadHistory();
  loadWeakTopics();
});
