# Coffee Ninja Hackathon

Coffee Ninja is an AI matching and activity coordination tool for the Linghang hackathon Coffee Ninja track.

The core idea: turn weak community ties into high-quality 1:1 or small-group conversations by understanding member intent, matching people with useful overlap, and making the next action frictionless.

## Hackathon Context

Linghang Hackathon, May 2, 2026, 13:30-17:00 at JJ Lake.

Coffee Ninja track:

> AI matching and activity coordination based on interests and current state, so weak ties can become high-quality connections.

## Problem

Communities usually have many people who would benefit from meeting each other, but most connections do not happen because:

- People do not know who else is relevant to their current goals.
- Organizers do not have time to manually pair members.
- Generic random coffee matching creates too many low-signal conversations.
- Even when a match is good, scheduling and conversation starts are awkward.
- The community rarely learns which matches worked and why.

## Product Thesis

Coffee Ninja should act like a lightweight community concierge:

1. Ask each member what they want right now.
2. Convert answers into structured interests, goals, availability, and social intent.
3. Recommend high-signal 1:1 or small-group matches.
4. Generate a warm intro and suggested activity.
5. Collect feedback to improve the next matching round.

## Product Boundary

Coffee Ninja is a professional meetup tool, not a dating app and not a job board.

Commonality:

- All three need profiles, preferences, matching, trust, consent, and feedback.
- All three reduce search costs by deciding who should meet whom.
- All three need to explain why a match is worth attention.

Differences:

- Professional meetup: the unit of value is a useful conversation, follow-up, or collaboration path.
- Dating app: the unit of value is mutual attraction, personal chemistry, and relationship intent.
- Job-seeking app: the unit of value is a hiring funnel event, such as referral, interview, or offer.

Coffee Ninja should optimize for professional intent fit, not attraction and not conversion to employment. A good match can be peer learning, a founder jam, advice, accountability, community onboarding, or a future collaboration. It does not need to become a date, an interview, or a transaction.

## MVP

The hackathon MVP can be built as a single web app:

- Member intake form: name, role, location, interests, goals, current state, availability, and preferred format.
- AI profile digestion: summarize each member into tags, intent, and connection needs.
- Matching engine: rank pairs or groups using overlap, complementarity, freshness, and availability.
- Intro generator: create a short reason for the match plus three conversation starters.
- Activity generator: suggest coffee, coworking, dinner, walk, founder jam, mock interview, or project pairing.
- Organizer dashboard: show proposed matches, confidence, rationale, and one-click export.
- Feedback loop: mark whether people met, whether it was useful, and what should be different next time.

## Definition of Done

The MVP is done when we can demonstrate one complete professional meetup cycle:

1. A member states a current professional intent in natural language.
2. Coffee Ninja extracts structured matching signals from that statement.
3. The system ranks at least five candidate matches or small groups.
4. Each recommendation includes a concrete reason, not generic overlap.
5. The organizer can approve, reject, or edit a match.
6. The system generates a warm intro and one suggested activity.
7. A lightweight feedback step records whether the match was useful.

If the demo only shows a list of people with shared tags, it is not done. The product must show how intent becomes a specific professional meeting with an explainable next step.

## Demo Flow

1. Add 8-12 sample community members.
2. Click "Run Coffee Ninja".
3. Show ranked matches with AI explanations.
4. Pick one match and generate a warm intro message.
5. Generate a mini activity plan based on both members' constraints.
6. Submit feedback and show how the next round changes.

## Matching Signals

Coffee Ninja should combine three types of signals:

- Similarity: shared interests, location, availability, language, event attendance.
- Complementarity: builder meets designer, founder meets investor, job seeker meets interviewer, newcomer meets veteran.
- Intent: what each person wants this week, such as brainstorming, accountability, hiring, learning, emotional support, or just meeting nearby people.

Example scoring:

```text
score = 0.35 * intent_fit
      + 0.25 * interest_overlap
      + 0.20 * complementarity
      + 0.10 * schedule_fit
      + 0.10 * freshness
```

## AI Behavior

The AI should not merely say "you both like AI." It should produce a concrete, human-readable reason:

```text
Yefei and Zara should meet because Yefei is exploring AI community tooling
and Zara has experience taking AI projects from 0 to 1. They both prefer
builder-focused conversations and are available Saturday afternoon. Suggested
activity: 30-minute coffee after demos, focused on turning the hackathon
prototype into a repeatable community workflow.
```

## Why Use an LLM

Without an LLM, Coffee Ninja becomes a tag-matching form. That is useful, but it misses the hardest part of professional meetup matching: people describe intent messily.

The LLM should be used for:

- Intent extraction: turn "I am stuck on GTM for my AI side project" into goals, stage, domain, and needed help.
- Profile normalization: map different wording into comparable signals without forcing every member into rigid dropdowns.
- Match explanation: produce a clear reason that helps both people say yes.
- Conversation design: generate agenda prompts that make the first 10 minutes productive.
- Feedback digestion: convert short post-meeting notes into better future matching constraints.

The LLM should not be used as a black-box decider. The ranking should still expose structured signals, scores, and organizer controls. The LLM adds judgment, language understanding, and explanation; the product still needs deterministic constraints for availability, repeats, blocks, and consent.

## Data Model

Minimum member fields:

- `id`
- `name`
- `role`
- `location`
- `interests`
- `skills`
- `current_goal`
- `current_state`
- `availability`
- `preferred_activity`
- `do_not_match_with`
- `past_matches`

Minimum match fields:

- `member_a`
- `member_b` or `group_members`
- `score`
- `match_reason`
- `conversation_starters`
- `suggested_activity`
- `intro_message`
- `status`
- `feedback`

## Implemented Skeleton

This repository now contains a lightweight FastAPI webapp with:

- Python backend in `backend/app`
- static frontend in `frontend`
- OpenAI Python SDK for profile extraction, match ranking, and match explanations
- Qdrant local vector DB for candidate profile retrieval
- seed profiles for a demo-ready matching pool
- deterministic local fallback when `OPENAI_API_KEY` is not configured

Run locally:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
PYTHONPATH=backend uvicorn app.main:app --reload
```

Then open `http://127.0.0.1:8000`.

Logs are written to both the terminal and `logs/coffee_ninja.log`.

Monitor logs in another terminal:

```bash
tail -f logs/coffee_ninja.log
```

Filter matching stages:

```bash
tail -f logs/coffee_ninja.log | grep 'matching.'
```

## Profile Process

Flow 1: onboarding.

1. User enters a professional value-exchange profile: name, headline, experience signals, what they can help with, what they want help with, conversation style, availability, interests, goals, and constraints.
2. Backend sends the raw intake to the OpenAI SDK.
3. LLM normalizes messy text into a `MemberProfile` with structured arrays and a concise `profile_summary`.
4. Backend builds `search_text` from the structured profile.
5. Backend embeds `search_text` and upserts the profile into Qdrant.
6. Frontend shows the generated profile JSON so the organizer can inspect what the system thinks it knows.

Profile output:

- `id`
- `name`
- `headline`
- `location`
- `availability`
- `can_help_with`
- `want_help_with`
- `company`
- `level`
- `years`
- `conversation_style`
- `interests`
- `expertise`
- `goals`
- `current_need`
- `preferred_formats`
- `constraints`
- `profile_summary`
- `search_text`
- `source`

## Matching Process

Flow 2: describe a need and generate matches.

1. User describes what they need right now in natural language.
2. Backend combines the user profile and current need into a retrieval query.
3. Backend embeds the query and searches Qdrant for relevant candidate profiles.
4. Backend sends the requester, need, and retrieved candidates to the OpenAI SDK.
5. LLM returns 2-3 ranked matches with grounded evidence, risks, suggested activity, conversation starters, and an intro message.
6. Frontend displays match cards that explain why each person is relevant using a value-exchange structure.

The backend matching flow has six logged stages:

1. `request`: receive the profile and current need.
2. `index_requester`: upsert the current requester profile into Qdrant so the latest profile is searchable.
3. `embed_query`: embed the requester's profile plus the current need.
4. `retrieve_candidates`: search Qdrant and filter out the requester.
5. `rank_candidates`: rank the retrieved candidates with the LLM, or local fallback if the LLM fails.
6. `response`: return 2-3 evidence-backed matches to the frontend.

Retrieval and ranking are intentionally separate:

- Retrieval is Qdrant-first. It produces a candidate pool using vector similarity and logs raw hits, filtered hits, candidate IDs, top scores, and duration.
- Ranking is LLM-first. It receives only the retrieved candidate pool and returns the final 2-3 matches with evidence, risks, suggested activity, and intro copy.
- Local ranking is a fallback path, not the main product behavior.

Match cards use the Claire demo structure:

- Match type: `Give-first match`, `Mutual exchange`, or `Peer match`
- `You want -> They did`
- `They want -> You have`
- Why this matters
- What to ask
- Interested action

Match output:

- `candidate_id`
- `candidate_name`
- `candidate_headline`
- `score`
- `match_type`
- `you_want`
- `they_did`
- `they_want`
- `you_have`
- `why_now`
- `why_this_matters`
- `evidence`
- `suggested_activity`
- `conversation_starters`
- `risks`
- `next_step_message`

## Chat Process

Flow 3: talk to a matched person.

The chat feature is intentionally lightweight. It is not a real-time websocket chat; it is a simple conversation and message manager for hackathon follow-up.

Backend responsibilities:

1. Create or reuse a two-person conversation.
2. List conversations for a participant.
3. Load one conversation and its message history.
4. Append messages to the conversation.
5. Persist conversations to `chat_data/conversations.json`.

Frontend responsibilities:

1. Reuse the onboarded profile as the current chat user.
2. Start a conversation manually or from a match card.
3. Show conversation list and selected thread.
4. Send short follow-up messages.

Chat endpoints:

- `GET /api/conversations?participant_id={id}`
- `POST /api/conversations`
- `GET /api/conversations/{conversation_id}`
- `POST /api/conversations/{conversation_id}/messages`

Generated chat data lives in `chat_data/`, which is ignored by git.

## Reference Products

These references shape the product direction:

- [Donut](https://www.donut.com/) shows that automated introductions work well inside existing team communication channels such as Slack or Teams, and that intro programs can scale beyond manual organizer work.
- [CoffeePals](https://help.coffeepals.com/en/article/how-to-set-up-coffeepals-in-slack-srblpn/) validates the recurring coffee-chat program model: opt-in audience, scheduled matching rounds, reminders, and simple setup.
- [Lunchclub](https://apps.apple.com/us/app/lunchclub-ai-networking-app/id1538817081) is a strong reference for goal-based AI networking where users describe professional goals and the system curates 1:1 meetings.
- [Aphinity](https://www.aphinity.ai/) is closest to the Coffee Ninja concept: AI-powered 1:1 introductions for communities, mentorship, onboarding, and professional networks, with profile questions, cadence, intro messages, and analytics.
- [Intros AI](https://www.intros.ai/) reinforces the community operating model: intro rounds, AI search across members, and analytics for who met whom.
- [Luma](https://help.luma.com/p/creating-an-event) is a reference for event creation, RSVP flow, approval, capacity, guest management, reminders, and post-event feedback.
- [Partiful](https://partiful.com/) is a reference for low-friction activity planning: one shareable invite link, RSVP tracking, guest visibility, reminders, and reusable social graphs.
- [ADPList](https://adplist.org/about-us) shows that structured matching and booking can scale human connection across mentorship and career growth communities.

## Silicon Valley Angle

In the Bay Area, the useful wedge is not "meet random people." The wedge is:

- Find the person who can unblock what I am working on this week.
- Turn event attendance into follow-up relationships.
- Help newcomers integrate into a high-context builder community faster.
- Make small gatherings self-organize from member intent.
- Give organizers visibility into which connections create repeat participation.

Coffee Ninja should feel like a community-native layer over Luma, Slack, Discord, Google Calendar, and group chats.

## Stretch Ideas

- Luma import: ingest event attendee lists and match people before or after an event.
- Slack or Discord bot: run `/coffee-ninja` to join the next round.
- Calendar-aware matching: suggest times based on availability windows.
- Warm intro sender: export to email, Slack DM, Discord DM, or WeChat copy.
- Community memory: avoid repeat matches unless both sides liked the previous one.
- Activity marketplace: turn clusters into small events like "AI builders coffee", "mock interview pod", or "founder problem clinic".
- Viral loop: every successful match can invite one new person into the next round.

## Suggested Tech Stack

For this hackathon prototype:

- Frontend: static HTML/CSS/JS served by FastAPI
- Backend: FastAPI
- Vector DB: local Qdrant file store
- AI: OpenAI Python SDK for profile extraction, match ranking, and intro generation
- Embeddings: OpenAI embeddings with local fallback for demo resilience

## Success Metrics

For a professional meetup, success is not "number of matches." A match only counts if it creates a useful professional interaction.

Primary success metric:

- Useful meeting rate: percent of approved matches where both sides say the conversation was worth their time.

Supporting metrics:

- Acceptance rate: percent of proposed matches accepted by both sides.
- Completion rate: percent of accepted matches that actually happen.
- Intent-fit rating: post-meeting score for whether the match addressed the stated professional goal.
- Follow-up rate: percent of meetings that create a next action, such as another call, intro, collaboration, resource share, or event invite.
- Newcomer activation: percent of new community members who complete at least one useful meeting.
- Cross-cluster bridges: number of matches between people who would not normally meet through existing friend groups.
- Organizer time saved: time needed to produce one matching round compared with manual pairing.
- Repeat participation: percent of members who opt into the next round after trying one match.

Anti-metrics:

- Matches generated but not accepted.
- Vague "you both like AI" rationales.
- Meetings that feel like unsolicited recruiting.
- Meetings that feel socially ambiguous or dating-like.
- High quantity with low follow-up.

Our current plan partially reflects this definition of done: it includes intake, matching, rationale, activity suggestions, and feedback. The weak point is that it needs to make professional outcome quality visible in the demo. The demo should show not just who matched, but why the match serves a stated goal and how feedback would improve the next round.

## One-Sentence Pitch

Coffee Ninja is an AI community concierge that matches members by real-time intent, generates warm intros and activity plans, and learns which connections actually become meaningful.
