from __future__ import annotations

import json

from app.core.config import settings
from app.schemas.match import CandidateMatch, MatchResponse
from app.schemas.profile import MemberProfile
from app.services.openai_service import OpenAIService
from app.services.profile_service import ProfileService
from app.services.text_utils import extract_json_object
from app.services.vector_store import VectorStore


class MatchingService:
    def __init__(self, profile_service: ProfileService) -> None:
        self.openai = OpenAIService()
        self.profile_service = profile_service
        self.vector_store = VectorStore()

    def match(self, profile: MemberProfile, need: str) -> MatchResponse:
        self.profile_service.index_profile(profile)
        query_text = f"{profile.search_text}\nCurrent matching request: {need}"
        query_vector = self.profile_service.embed_query(query_text)
        retrieved = [
            hit
            for hit in self.vector_store.search(query_vector, top_k=settings.retrieval_top_k)
            if hit["payload"].get("id") != profile.id
        ]
        candidates = retrieved[:6]

        if self.openai.enabled and candidates:
            try:
                return self._rank_with_llm(profile, need, candidates)
            except Exception:
                pass

        return self._rank_locally(profile, need, candidates)

    def _rank_with_llm(self, profile: MemberProfile, need: str, candidates: list[dict]) -> MatchResponse:
        schema = MatchResponse.model_json_schema()
        instructions = """
You are Coffee Ninja's professional meetup matching agent.
Rank candidates for useful professional conversations, not dating and not recruiting.
Return 2 or 3 matches. Every match must include evidence grounded in the candidate payload,
a practical activity, risks, and a ready-to-send intro message.
"""
        payload = {
            "requester": profile.model_dump(),
            "need": need,
            "retrieved_candidates": candidates,
        }
        output = self.openai.generate_json(
            instructions=instructions.strip(),
            input_text=json.dumps(payload, ensure_ascii=False),
            schema=schema,
            name="coffee_match_response",
        )
        data = extract_json_object(output)
        return MatchResponse(**data)

    def _rank_locally(self, profile: MemberProfile, need: str, candidates: list[dict]) -> MatchResponse:
        requester_terms = {
            *(item.lower() for item in profile.interests),
            *(item.lower() for item in profile.expertise),
            *(item.lower() for item in profile.goals),
            *need.lower().replace("/", " ").replace(",", " ").split(),
        }

        matches: list[CandidateMatch] = []
        for hit in candidates[:3]:
            candidate = hit["payload"]
            candidate_terms = {
                *(item.lower() for item in candidate.get("interests", [])),
                *(item.lower() for item in candidate.get("expertise", [])),
                *(item.lower() for item in candidate.get("goals", [])),
            }
            overlap = sorted(term for term in requester_terms.intersection(candidate_terms) if len(term) > 2)
            evidence = [
                f"Vector retrieval score: {hit['score']:.2f}",
                f"{candidate.get('name')} focuses on {candidate.get('profile_summary')}",
            ]
            if overlap:
                evidence.append(f"Shared signals: {', '.join(overlap[:4])}")

            matches.append(
                CandidateMatch(
                    candidate_id=candidate.get("id", ""),
                    candidate_name=candidate.get("name", ""),
                    candidate_headline=candidate.get("headline", ""),
                    score=round(float(hit["score"]), 3),
                    match_type="Professional intent fit",
                    why_now=f"{candidate.get('name')} appears relevant to: {need}",
                    evidence=evidence,
                    suggested_activity=self._activity(candidate),
                    conversation_starters=[
                        f"What would make this conversation useful for {profile.name}'s current request?",
                        f"Where does {candidate.get('name')}'s experience most directly apply?",
                        "What is one concrete follow-up both sides can decide within 30 minutes?",
                    ],
                    risks=["Confirm this does not become a generic recruiting or sales conversation."],
                    next_step_message=(
                        f"Intro: {profile.name}, meet {candidate.get('name')}. "
                        f"You both have signals around {', '.join(overlap[:2]) or 'applied AI/community work'}, "
                        f"and the suggested focus is: {need}"
                    ),
                )
            )

        return MatchResponse(
            query_summary=f"{profile.name} is looking for: {need}",
            matches=matches,
            used_llm=False,
        )

    def _activity(self, candidate: dict) -> str:
        formats = candidate.get("preferred_formats") or ["coffee"]
        return f"30-minute {formats[0]} focused on one concrete professional next step."
