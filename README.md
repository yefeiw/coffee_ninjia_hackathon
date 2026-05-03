# Coffee Ninja Hackathon

Coffee Ninja is an AI matching and activity coordination tool for the Linghang hackathon Coffee Ninja track.

This README is the **uber doc** for the project. It gives the quick-start path and links to deeper docs in `docs/`.

---

## 1) What We Are Building

Coffee Ninja turns weak community ties into high-quality professional conversations:

1. Capture current intent from each member.
2. Structure that intent into matchable fields.
3. Retrieve and rank relevant candidates.
4. Generate a warm intro and suggested next action.
5. Record lightweight feedback for iterative improvement.

Coffee Ninja is a **professional meetup tool**, not a dating app and not a job board.

---

## 2) Hackathon Scope and Constraint

- Event context: Linghang Hackathon (Coffee Ninja track)
- Hard constraint: a compelling, reliable demo in ~90 minutes
- Product bar for the demo:
  - onboarding works
  - matching works
  - explanation is concrete
  - conversation handoff works

---

## 3) Architecture at a Glance

- **Backend**: FastAPI (`backend/app`)
- **Frontend**: static HTML/CSS/JS (`frontend`)
- **LLM + Embeddings**: OpenAI Python SDK
- **Retrieval**: Qdrant local vector DB (`:memory:`)
- **Fallback mode**: deterministic local behavior when `OPENAI_API_KEY` is not set
- **Chat persistence**: local JSON file

Primary API flow:
- `POST /api/onboarding` -> intake to structured profile
- `POST /api/matches` -> retrieval + ranking + rationale
- `POST /api/conversations` and `POST /api/conversations/{id}/messages` -> chat loop

---

## 4) Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=backend uvicorn app.main:app --reload
```

Open:
- App: `http://127.0.0.1:8000`
- Admin: `http://127.0.0.1:8000/admin`

---

## 5) Seeding Demo Data

Use the seed endpoint to populate demo profiles:

```bash
curl -X POST http://127.0.0.1:8000/api/seed
```

Then verify seeded profiles in admin or via API:

```bash
curl http://127.0.0.1:8000/api/admin/profiles
```

---

## 6) Testing / Validation Checklist

Backend smoke checks:

```bash
curl http://127.0.0.1:8000/health
curl -X POST http://127.0.0.1:8000/api/seed
curl http://127.0.0.1:8000/api/admin/profiles
```

Functional demo checks:
1. Submit onboarding form.
2. Submit matching request.
3. Confirm 2-3 recommendations with rationale.
4. Create conversation and send one message.

Fallback checks:
- Unset `OPENAI_API_KEY` and verify local fallback still returns a valid match response.

---

## 7) Documentation Map (`docs/`)

- `docs/product.md` — product framing, scope, and success criteria
- `docs/tech_design.md` — system design, service boundaries, data flow
- `docs/ui.md` — UX flow, screen structure, and copy strategy
- `docs/progress_log.md` — implementation timeline and decision log

When the code changes, update relevant docs so the README + docs remain accurate.

---

## 8) Repository Layout

```text
backend/
  app/
frontend/
profile_data/
docs/
README.md
AGENTS.md
```

---

## 9) Extended Notes

For richer product narrative and matching details, see `docs/product.md` and `docs/tech_design.md`.
