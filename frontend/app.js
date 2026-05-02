const state = {
  profile: JSON.parse(localStorage.getItem("coffee_ninja_profile") || "null"),
};

const modelStatus = document.querySelector("#modelStatus");
const profileForm = document.querySelector("#profileForm");
const matchForm = document.querySelector("#matchForm");
const profileResult = document.querySelector("#profileResult");
const matchResult = document.querySelector("#matchResult");

document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((item) => item.classList.remove("active"));
    document.querySelectorAll(".panel").forEach((panel) => panel.classList.remove("active"));
    tab.classList.add("active");
    document.querySelector(`#${tab.dataset.panel}`).classList.add("active");
  });
});

async function checkHealth() {
  try {
    const response = await fetch("/health");
    if (!response.ok) throw new Error("Backend unavailable");
    modelStatus.textContent = "Backend ready";
  } catch (error) {
    modelStatus.textContent = "Backend offline";
  }
}

profileForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = Object.fromEntries(new FormData(profileForm).entries());
  profileResult.hidden = false;
  profileResult.innerHTML = "<p>Generating structured profile...</p>";

  try {
    const response = await fetch("/api/onboarding", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Profile generation failed");
    state.profile = data.profile;
    localStorage.setItem("coffee_ninja_profile", JSON.stringify(state.profile));
    renderProfile(data.profile, data.used_llm);
  } catch (error) {
    profileResult.innerHTML = `<p class="warning">${escapeHtml(error.message)}</p>`;
  }
});

matchForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!state.profile) {
    matchResult.hidden = false;
    matchResult.innerHTML = '<p class="warning">Generate a profile before matching.</p>';
    return;
  }

  const payload = {
    profile: state.profile,
    need: new FormData(matchForm).get("need"),
  };
  matchResult.hidden = false;
  matchResult.innerHTML = "<p>Searching Qdrant and generating match evidence...</p>";

  try {
    const response = await fetch("/api/matches", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Match generation failed");
    renderMatches(data);
  } catch (error) {
    matchResult.innerHTML = `<p class="warning">${escapeHtml(error.message)}</p>`;
  }
});

function renderProfile(profile, usedLlm) {
  profileResult.innerHTML = `
    <div class="profileSummary">
      <h3>${escapeHtml(profile.name)}</h3>
      <p>${escapeHtml(profile.headline)}</p>
      <p>${escapeHtml(profile.profile_summary)}</p>
      <div class="meta">
        <span class="pill">${usedLlm ? "LLM structured" : "Local fallback"}</span>
        <span class="pill">${escapeHtml(profile.location || "No location")}</span>
        <span class="pill">${escapeHtml(profile.availability || "No availability")}</span>
      </div>
    </div>
    <pre>${escapeHtml(JSON.stringify(profile, null, 2))}</pre>
  `;
}

function renderMatches(data) {
  const cards = data.matches
    .map(
      (match) => `
        <article class="matchCard">
          <h3>${escapeHtml(match.candidate_name)}</h3>
          <p>${escapeHtml(match.candidate_headline)}</p>
          <p class="score">Score ${Number(match.score).toFixed(2)} · ${escapeHtml(match.match_type)}</p>
          <p>${escapeHtml(match.why_now)}</p>
          <h3>Evidence</h3>
          <ul>${match.evidence.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
          <h3>Activity</h3>
          <p>${escapeHtml(match.suggested_activity)}</p>
          <h3>Starters</h3>
          <ul>${match.conversation_starters.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
          <h3>Intro</h3>
          <p>${escapeHtml(match.next_step_message)}</p>
        </article>
      `,
    )
    .join("");

  matchResult.innerHTML = `
    <div class="profileSummary">
      <h3>${escapeHtml(data.query_summary)}</h3>
      <div class="meta">
        <span class="pill">${data.used_llm ? "LLM ranked" : "Local fallback"}</span>
        <span class="pill">Qdrant retrieval</span>
      </div>
    </div>
    <div class="matchGrid">${cards}</div>
  `;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

if (state.profile) {
  profileResult.hidden = false;
  renderProfile(state.profile, false);
}

checkHealth();
