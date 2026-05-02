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

## MVP

The hackathon MVP can be built as a single web app:

- Member intake form: name, role, location, interests, goals, current state, availability, and preferred format.
- AI profile digestion: summarize each member into tags, intent, and connection needs.
- Matching engine: rank pairs or groups using overlap, complementarity, freshness, and availability.
- Intro generator: create a short reason for the match plus three conversation starters.
- Activity generator: suggest coffee, coworking, dinner, walk, founder jam, mock interview, or project pairing.
- Organizer dashboard: show proposed matches, confidence, rationale, and one-click export.
- Feedback loop: mark whether people met, whether it was useful, and what should be different next time.

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

For a fast hackathon prototype:

- Frontend: Next.js or Vite React
- Backend: FastAPI or Next.js API routes
- Storage: SQLite, Supabase, or local JSON for demo
- AI: OpenAI API for profile extraction, match rationale, and intro generation
- Embeddings: optional, for interest similarity search

## Success Metrics

- Match acceptance rate
- Meeting completion rate
- Post-meeting usefulness rating
- Number of second-order intros created
- Repeat participation in future rounds
- Organizer time saved per matching cycle

## One-Sentence Pitch

Coffee Ninja is an AI community concierge that matches members by real-time intent, generates warm intros and activity plans, and learns which connections actually become meaningful.
