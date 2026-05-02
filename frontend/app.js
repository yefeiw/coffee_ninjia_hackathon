const state = {
  profile: JSON.parse(localStorage.getItem("coffee_ninja_profile") || "null"),
  activeConversation: null,
  conversations: [],
  interestedMatches: JSON.parse(localStorage.getItem("coffee_ninja_interested") || "{}"),
};

const modelStatus = document.querySelector("#modelStatus");
const profileForm = document.querySelector("#profileForm");
const matchForm = document.querySelector("#matchForm");
const conversationForm = document.querySelector("#conversationForm");
const messageForm = document.querySelector("#messageForm");
const refreshConversationsButton = document.querySelector("#refreshConversationsButton");
const profileResult = document.querySelector("#profileResult");
const matchResult = document.querySelector("#matchResult");
const conversationList = document.querySelector("#conversationList");
const threadHeader = document.querySelector("#threadHeader");
const messageList = document.querySelector("#messageList");

document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((item) => item.classList.remove("active"));
    document.querySelectorAll(".panel").forEach((panel) => panel.classList.remove("active"));
    tab.classList.add("active");
    document.querySelector(`#${tab.dataset.panel}`).classList.add("active");
    if (tab.dataset.panel === "chatPanel") {
      syncChatIdentityFields();
      loadConversations();
    }
  });
});

document.querySelectorAll(".chipGroup").forEach((group) => {
  const input = profileForm.elements[group.dataset.chipTarget];
  syncChipsFromInput(group, input);
  group.addEventListener("click", (event) => {
    const button = event.target.closest("button[data-value]");
    if (!button) return;
    if (group.classList.contains("single")) {
      group.querySelectorAll("button").forEach((item) => item.classList.remove("selected"));
      button.classList.add("selected");
      input.value = button.dataset.value;
      return;
    }
    button.classList.toggle("selected");
    input.value = Array.from(group.querySelectorAll(".selected"))
      .map((item) => item.dataset.value)
      .join(", ");
  });
});

document.addEventListener("click", (event) => {
  const chatButton = event.target.closest("[data-start-chat]");
  const interestedButton = event.target.closest("[data-interested]");
  if (interestedButton) {
    state.interestedMatches[interestedButton.dataset.candidateId] = true;
    localStorage.setItem("coffee_ninja_interested", JSON.stringify(state.interestedMatches));
    const status = document.querySelector(
      `[data-interest-status="${CSS.escape(interestedButton.dataset.candidateId)}"]`,
    );
    if (status) {
      status.textContent = "Interested noted. Warm intro is ready.";
      status.hidden = false;
    }
    return;
  }
  if (!chatButton) return;
  syncChatIdentityFields();
  conversationForm.elements.other_id.value = chatButton.dataset.candidateId;
  conversationForm.elements.other_name.value = chatButton.dataset.candidateName;
  conversationForm.elements.title.value = `Coffee follow-up with ${chatButton.dataset.candidateName}`;
  document.querySelector('[data-panel="chatPanel"]').click();
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
    syncChatIdentityFields();
    renderProfile(data.profile, data.used_llm);
  } catch (error) {
    profileResult.innerHTML = `<p class="warning">${escapeHtml(error.message)}</p>`;
  }
});

conversationForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = new FormData(conversationForm);
  const payload = {
    participant_a: {
      id: form.get("my_id"),
      name: form.get("my_name"),
      headline: state.profile?.headline || "",
    },
    participant_b: {
      id: form.get("other_id"),
      name: form.get("other_name"),
      headline: "",
    },
    title: form.get("title"),
  };

  try {
    const response = await fetch("/api/conversations", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Conversation creation failed");
    state.activeConversation = data;
    await loadConversations();
    renderConversation(data);
  } catch (error) {
    threadHeader.textContent = error.message;
  }
});

refreshConversationsButton.addEventListener("click", () => {
  syncChatIdentityFields();
  loadConversations();
});

messageForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!state.activeConversation) {
    threadHeader.textContent = "Open a conversation before sending.";
    return;
  }
  const body = new FormData(messageForm).get("body");
  const sender = currentChatIdentity();
  const payload = {
    sender_id: sender.id,
    sender_name: sender.name,
    body,
  };

  try {
    const response = await fetch(`/api/conversations/${state.activeConversation.id}/messages`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Message send failed");
    state.activeConversation = data;
    messageForm.reset();
    renderConversation(data);
    await loadConversations();
  } catch (error) {
    threadHeader.textContent = error.message;
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
        <span class="pill">${escapeHtml(profile.conversation_style || "No style")}</span>
      </div>
      <div class="valueGrid">
        <div><strong>I can help with</strong><p>${escapeHtml((profile.can_help_with || []).join(", ") || "Not set")}</p></div>
        <div><strong>I want help with</strong><p>${escapeHtml((profile.want_help_with || []).join(", ") || "Not set")}</p></div>
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
          <div class="meta">
            <span class="pill">${escapeHtml(match.match_type)}</span>
            <span class="pill">Score ${Number(match.score).toFixed(2)}</span>
          </div>
          <div class="exchangeGrid">
            <div><strong>You want</strong><p>${escapeHtml(match.you_want || "A useful professional conversation")}</p></div>
            <div><strong>They did</strong><p>${escapeHtml(match.they_did || match.why_now)}</p></div>
            <div><strong>They want</strong><p>${escapeHtml(match.they_want || "A relevant professional exchange")}</p></div>
            <div><strong>You have</strong><p>${escapeHtml(match.you_have || "Applied AI and community context")}</p></div>
          </div>
          <h3>Why this matters</h3>
          <p>${escapeHtml(match.why_this_matters || match.why_now)}</p>
          <h3>Evidence</h3>
          <ul>${match.evidence.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
          <h3>Activity</h3>
          <p>${escapeHtml(match.suggested_activity)}</p>
          <h3>Starters</h3>
          <ul>${match.conversation_starters.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
          <h3>Intro</h3>
          <p>${escapeHtml(match.next_step_message)}</p>
          <p class="interestStatus" data-interest-status="${escapeHtml(match.candidate_id)}" ${state.interestedMatches[match.candidate_id] ? "" : "hidden"}>Interested noted. Warm intro is ready.</p>
          <button type="button" data-interested data-candidate-id="${escapeHtml(match.candidate_id)}">
            Interested
          </button>
          <button
            type="button"
            data-start-chat
            data-candidate-id="${escapeHtml(match.candidate_id)}"
            data-candidate-name="${escapeHtml(match.candidate_name)}"
          >Start Chat</button>
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

async function loadConversations() {
  const identity = currentChatIdentity();
  const query = identity.id ? `?participant_id=${encodeURIComponent(identity.id)}` : "";
  conversationList.innerHTML = "<p>Loading conversations...</p>";

  try {
    const response = await fetch(`/api/conversations${query}`);
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Conversation load failed");
    state.conversations = data;
    renderConversationList(data);
  } catch (error) {
    conversationList.innerHTML = `<p class="warning">${escapeHtml(error.message)}</p>`;
  }
}

async function openConversation(conversationId) {
  const response = await fetch(`/api/conversations/${conversationId}`);
  const data = await response.json();
  if (!response.ok) {
    threadHeader.textContent = data.detail || "Conversation load failed";
    return;
  }
  state.activeConversation = data;
  renderConversation(data);
}

function renderConversationList(conversations) {
  if (!conversations.length) {
    conversationList.innerHTML = "<p>No conversations yet.</p>";
    return;
  }

  conversationList.innerHTML = conversations
    .map(
      (conversation) => `
        <button class="conversationItem" type="button" data-conversation-id="${escapeHtml(conversation.id)}">
          <span>${escapeHtml(conversation.title)}</span>
          <small>${conversation.message_count} messages</small>
        </button>
      `,
    )
    .join("");

  conversationList.querySelectorAll("[data-conversation-id]").forEach((button) => {
    button.addEventListener("click", () => openConversation(button.dataset.conversationId));
  });
}

function renderConversation(conversation) {
  threadHeader.textContent = conversation.title;
  if (!conversation.messages.length) {
    messageList.innerHTML = "<p>No messages yet. Send the first follow-up.</p>";
    return;
  }

  messageList.innerHTML = conversation.messages
    .map(
      (message) => `
        <div class="messageBubble ${message.sender_id === currentChatIdentity().id ? "mine" : ""}">
          <div class="messageMeta">${escapeHtml(message.sender_name)} · ${formatDate(message.created_at)}</div>
          <div>${escapeHtml(message.body)}</div>
        </div>
      `,
    )
    .join("");
  messageList.scrollTop = messageList.scrollHeight;
}

function syncChatIdentityFields() {
  const identity = currentChatIdentity();
  conversationForm.elements.my_id.value = identity.id;
  conversationForm.elements.my_name.value = identity.name;
}

function currentChatIdentity() {
  return {
    id: state.profile?.id || conversationForm?.elements.my_id.value || "user_demo",
    name: state.profile?.name || conversationForm?.elements.my_name.value || "Demo User",
  };
}

function formatDate(value) {
  return new Date(value).toLocaleString([], {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function syncChipsFromInput(group, input) {
  const selected = new Set(
    String(input.value || "")
      .split(",")
      .map((item) => item.trim().toLowerCase())
      .filter(Boolean),
  );
  group.querySelectorAll("button[data-value]").forEach((button) => {
    if (selected.has(button.dataset.value.toLowerCase())) {
      button.classList.add("selected");
    }
  });
}

if (state.profile) {
  profileResult.hidden = false;
  renderProfile(state.profile, false);
  syncChatIdentityFields();
}

checkHealth();
