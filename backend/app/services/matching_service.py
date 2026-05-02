from __future__ import annotations

import json
import logging
import time

from app.core.config import settings
from app.schemas.match import CandidateMatch, MatchResponse
from app.schemas.profile import MemberProfile
from app.services.openai_service import OpenAIService
from app.services.profile_service import ProfileService
from app.services.text_utils import extract_json_object
from app.services.vector_store import VectorStore


logger = logging.getLogger(__name__)


class MatchingService:
    def __init__(self, profile_service: ProfileService) -> None:
        self.openai = OpenAIService()
        self.profile_service = profile_service
        self.vector_store = VectorStore()

    def match(self, profile: MemberProfile, need: str) -> MatchResponse:
        request_started = time.perf_counter()
        logger.info(
            "matching.stage.start stage=request profile_id=%s need_chars=%s",
            profile.id,
            len(need),
        )

        stage_started = time.perf_counter()
        self.profile_service.index_profile(profile)
        logger.info(
            "matching.stage.done stage=index_requester profile_id=%s duration_ms=%s",
            profile.id,
            self._duration_ms(stage_started),
        )

        stage_started = time.perf_counter()
        query_text = f"{profile.search_text}\nCurrent matching request: {need}"
        query_vector = self.profile_service.embed_query(query_text)
        logger.info(
            "matching.stage.done stage=embed_query profile_id=%s query_chars=%s vector_size=%s duration_ms=%s",
            profile.id,
            len(query_text),
            len(query_vector),
            self._duration_ms(stage_started),
        )

        stage_started = time.perf_counter()
        raw_hits = self._retrieve_candidates(query_vector)
        retrieved = [
            hit
            for hit in raw_hits
            if not self._is_requester_duplicate(profile, hit["payload"])
        ]
        candidates = retrieved[:6]
        logger.info(
            "matching.stage.done stage=retrieve_candidates profile_id=%s raw_hits=%s filtered_hits=%s candidate_ids=%s duration_ms=%s",
            profile.id,
            len(raw_hits),
            len(candidates),
            [hit["payload"].get("id") for hit in candidates],
            self._duration_ms(stage_started),
        )

        if self.openai.enabled and candidates:
            try:
                stage_started = time.perf_counter()
                response = self._rank_with_llm(profile, need, candidates)
                logger.info(
                    "matching.stage.done stage=rank_candidates ranker=llm profile_id=%s matches=%s match_ids=%s duration_ms=%s total_duration_ms=%s",
                    profile.id,
                    len(response.matches),
                    [match.candidate_id for match in response.matches],
                    self._duration_ms(stage_started),
                    self._duration_ms(request_started),
                )
                return response
            except Exception:
                logger.exception(
                    "matching.stage.failed stage=rank_candidates ranker=llm profile_id=%s fallback=local",
                    profile.id,
                )

        stage_started = time.perf_counter()
        response = self._rank_locally(profile, need, candidates)
        logger.info(
            "matching.stage.done stage=rank_candidates ranker=local profile_id=%s matches=%s match_ids=%s duration_ms=%s total_duration_ms=%s",
            profile.id,
            len(response.matches),
            [match.candidate_id for match in response.matches],
            self._duration_ms(stage_started),
            self._duration_ms(request_started),
        )
        return response

    def _retrieve_candidates(self, query_vector: list[float]) -> list[dict]:
        logger.info(
            "matching.retrieval.start top_k=%s vector_size=%s",
            settings.retrieval_top_k,
            len(query_vector),
        )
        hits = self.vector_store.search(query_vector, top_k=settings.retrieval_top_k)
        logger.info(
            "matching.retrieval.done hits=%s candidate_ids=%s",
            len(hits),
            [hit["payload"].get("id") for hit in hits[:6]],
        )
        return hits

    def _is_requester_duplicate(self, profile: MemberProfile, candidate_payload: dict) -> bool:
        if candidate_payload.get("id") == profile.id:
            return True
        return self._normalize_name(candidate_payload.get("name", "")) == self._normalize_name(profile.name)

    def _normalize_name(self, name: str) -> str:
        return " ".join(name.lower().split())

    def _rank_with_llm(self, profile: MemberProfile, need: str, candidates: list[dict]) -> MatchResponse:
        logger.info(
            "matching.ranking.llm.start profile_id=%s candidates=%s candidate_ids=%s",
            profile.id,
            len(candidates),
            [candidate["payload"].get("id") for candidate in candidates],
        )
        schema = MatchResponse.model_json_schema()
        instructions = """
You are Coffee Ninja's professional meetup matching agent.
Rank candidates for useful professional conversations, not dating and not recruiting.
Return 2 or 3 matches. Every match must include evidence grounded in the candidate payload,
a practical activity, risks, and a ready-to-send intro message.
match_type must be one of: Give-first match, Mutual exchange, Peer match.
For every match, fill these product demo fields:
- you_want: what the requester wants help with
- they_did: what the candidate has actually done that maps to that need
- they_want: what the candidate wants help with
- you_have: what the requester can offer back
- why_this_matters: why this is worth a 30-minute professional conversation
"""
        payload = {
            "requester": profile.model_dump(),
            "need": need,
            "retrieved_candidates": self._candidate_payloads_for_ranking(candidates),
        }
        output = self.openai.generate_json(
            instructions=instructions.strip(),
            input_text=json.dumps(payload, ensure_ascii=False),
            schema=schema,
            name="coffee_match_response",
        )
        data = extract_json_object(output)
        response = MatchResponse(**data)
        logger.info(
            "matching.ranking.llm.done profile_id=%s matches=%s match_ids=%s used_llm=%s",
            profile.id,
            len(response.matches),
            [match.candidate_id for match in response.matches],
            response.used_llm,
        )
        return response

    def _rank_locally(self, profile: MemberProfile, need: str, candidates: list[dict]) -> MatchResponse:
        logger.info(
            "matching.ranking.local.start profile_id=%s candidates=%s candidate_ids=%s",
            profile.id,
            len(candidates),
            [candidate["payload"].get("id") for candidate in candidates],
        )
        requester_terms = {
            *(item.lower() for item in profile.can_help_with),
            *(item.lower() for item in profile.want_help_with),
            *(item.lower() for item in profile.interests),
            *(item.lower() for item in profile.expertise),
            *(item.lower() for item in profile.goals),
            *need.lower().replace("/", " ").replace(",", " ").split(),
        }

        matches: list[CandidateMatch] = []
        for hit in candidates[:3]:
            candidate = hit["payload"]
            candidate_terms = {
                *(item.lower() for item in candidate.get("can_help_with", [])),
                *(item.lower() for item in candidate.get("want_help_with", [])),
                *(item.lower() for item in candidate.get("interests", [])),
                *(item.lower() for item in candidate.get("expertise", [])),
                *(item.lower() for item in candidate.get("goals", [])),
            }
            match_type = self._match_type(profile, candidate)
            you_want = self._first(profile.want_help_with, need)
            they_did = self._first(candidate.get("can_help_with", []), candidate.get("profile_summary", ""))
            they_want = self._first(candidate.get("want_help_with", []), candidate.get("current_need", ""))
            you_have = self._first(profile.can_help_with, profile.profile_summary)
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
                    match_type=match_type,
                    you_want=you_want,
                    they_did=they_did,
                    they_want=they_want,
                    you_have=you_have,
                    why_now=f"{candidate.get('name')} appears relevant to: {need}",
                    why_this_matters=self._why_this_matters(match_type, candidate),
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

        response = MatchResponse(
            query_summary=f"{profile.name} is looking for: {need}",
            matches=matches,
            used_llm=False,
        )
        logger.info(
            "matching.ranking.local.done profile_id=%s matches=%s match_ids=%s",
            profile.id,
            len(response.matches),
            [match.candidate_id for match in response.matches],
        )
        return response

    def _activity(self, candidate: dict) -> str:
        formats = candidate.get("preferred_formats") or ["coffee"]
        return f"30-minute {formats[0]} focused on one concrete professional next step."

    def _candidate_payloads_for_ranking(self, candidates: list[dict]) -> list[dict]:
        ranked_candidates: list[dict] = []
        for candidate in candidates:
            payload = dict(candidate["payload"])
            payload["retrieval_score"] = round(float(candidate["score"]), 3)
            ranked_candidates.append(payload)
        return ranked_candidates

    def _match_type(self, profile: MemberProfile, candidate: dict) -> str:
        requester_can_help = bool(profile.can_help_with)
        requester_wants = bool(profile.want_help_with or profile.current_need)
        candidate_can_help = bool(candidate.get("can_help_with"))
        candidate_wants = bool(candidate.get("want_help_with") or candidate.get("current_need"))

        if requester_can_help and requester_wants and candidate_can_help and candidate_wants:
            return "Mutual exchange"
        if candidate_can_help and requester_wants:
            return "Give-first match"
        return "Peer match"

    def _why_this_matters(self, match_type: str, candidate: dict) -> str:
        if match_type == "Mutual exchange":
            return "Both sides have a concrete ask and a concrete give, so the conversation can create value quickly."
        if match_type == "Give-first match":
            return f"{candidate.get('name')} has relevant experience for the request and can make the first conversation immediately useful."
        return "Both people are close enough in context to compare notes, unblock each other, and keep the conversation low-friction."

    def _first(self, values: list[str] | str, fallback: str) -> str:
        if isinstance(values, list) and values:
            return values[0]
        if isinstance(values, str) and values:
            return values
        return fallback

    def _duration_ms(self, started_at: float) -> int:
        return round((time.perf_counter() - started_at) * 1000)
