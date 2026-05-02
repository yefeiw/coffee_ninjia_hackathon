# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Coffee Ninja is an AI-powered matching and activity coordination tool for professional communities. It matches members by real-time intent, generates warm intros and activity plans, and learns from feedback. Built for the Linghang Hackathon (May 2, 2026).

This is **not** a dating app or job board. The unit of value is a useful professional conversation, follow-up, or collaboration path.

## Current State

Greenfield project — the repo currently contains only the product specification in README.md. No code, no build system, no dependencies yet.

## Suggested Tech Stack (from spec)

- Frontend: Next.js or Vite + React
- Backend: FastAPI or Next.js API routes
- Storage: SQLite, Supabase, or local JSON (demo-grade)
- AI: OpenAI API (profile extraction, match rationale, intro generation)
- Embeddings: optional, for interest similarity search

## Architecture (Planned)

The MVP is a single web app with these layers:

1. **Member intake** — form collecting name, role, location, interests, skills, current goal/state, availability, preferred activity, exclusions, past matches
2. **AI profile digestion** — LLM extracts structured tags, intent, and connection needs from natural language input
3. **Matching engine** — deterministic scoring with LLM-enhanced judgment:
   ```
   score = 0.35 * intent_fit + 0.25 * interest_overlap + 0.20 * complementarity + 0.10 * schedule_fit + 0.10 * freshness
   ```
4. **Intro & activity generator** — LLM produces concrete match reasons, conversation starters, and activity suggestions
5. **Organizer dashboard** — shows ranked matches with confidence, rationale, approve/reject/edit controls
6. **Feedback loop** — post-meeting usefulness ratings that improve future rounds

Key design constraint: the LLM adds judgment and explanation, but ranking must expose structured signals, scores, and organizer controls. No black-box decisions.

## Key Domain Rules

- Match rationales must be specific and actionable ("Yefei is exploring AI community tooling and Zara has experience taking AI projects from 0 to 1"), never generic ("you both like AI")
- Matches should optimize for professional intent fit: peer learning, founder jams, advice, accountability, community onboarding, future collaboration
- Organizers must be able to approve, reject, or edit any match
- System must respect do-not-match exclusions and avoid repeating matches unless both sides liked the previous one

## Definition of Done (MVP)

A complete cycle: member states intent -> system extracts signals -> ranks 5+ matches -> each has concrete reason -> organizer can approve/reject/edit -> warm intro + activity generated -> feedback recorded. If it only shows shared tags, it's not done.
