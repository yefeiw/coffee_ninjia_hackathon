from __future__ import annotations

import json
import logging
import uuid

from app.data.sample_profiles import SAMPLE_PROFILES
from app.schemas.profile import MemberProfile, ProfileIntake
from app.services.openai_service import OpenAIService
from app.services.text_utils import extract_json_object, local_embedding, profile_search_text, split_terms
from app.services.vector_store import VectorStore


logger = logging.getLogger(__name__)


class ProfileService:
    def __init__(self) -> None:
        self.openai = OpenAIService()
        self.vector_store = VectorStore()

    def seed_profiles(self) -> None:
        logger.info("profile.seed.start count=%s", len(SAMPLE_PROFILES))
        for raw_profile in SAMPLE_PROFILES:
            profile = self._hydrate_seed_profile(raw_profile)
            self.index_profile(profile)
        logger.info("profile.seed.done count=%s", len(SAMPLE_PROFILES))

    def create_profile(self, intake: ProfileIntake) -> tuple[MemberProfile, bool]:
        used_llm = False
        if self.openai.enabled:
            try:
                logger.info("profile.create.llm.start name=%s", intake.name)
                profile = self._create_profile_with_llm(intake)
                used_llm = True
                logger.info("profile.create.llm.done profile_id=%s", profile.id)
            except Exception:
                logger.exception("profile.create.llm.failed name=%s fallback=local", intake.name)
                profile = self._create_profile_locally(intake)
        else:
            logger.info("profile.create.local.start name=%s reason=no_openai_key", intake.name)
            profile = self._create_profile_locally(intake)

        self.index_profile(profile)
        return profile, used_llm

    def index_profile(self, profile: MemberProfile) -> None:
        logger.info(
            "profile.index.start profile_id=%s source=%s search_text_chars=%s",
            profile.id,
            profile.source,
            len(profile.search_text),
        )
        vector = self._embed_text(profile.search_text)
        logger.info(
            "profile.index.embedding.done profile_id=%s vector_size=%s",
            profile.id,
            len(vector),
        )
        self.vector_store.upsert_profile(
            profile_id=profile.id,
            vector=vector,
            payload=profile.model_dump(),
        )
        logger.info("profile.index.done profile_id=%s", profile.id)

    def embed_query(self, text: str) -> list[float]:
        return self._embed_text(text)

    def _embed_text(self, text: str) -> list[float]:
        if self.openai.enabled:
            try:
                logger.info("embedding.openai.start text_chars=%s", len(text))
                return self.openai.embed_text(text)
            except Exception:
                logger.exception("embedding.openai.failed fallback=local text_chars=%s", len(text))
                return local_embedding(text)
        logger.info("embedding.local.start text_chars=%s reason=no_openai_key", len(text))
        return local_embedding(text)

    def _create_profile_with_llm(self, intake: ProfileIntake) -> MemberProfile:
        schema = MemberProfile.model_json_schema()
        instructions = """
You extract professional meetup profiles for Coffee Ninja.
This is not dating and not recruiting. Optimize for useful professional conversations.
Return only JSON that matches the schema. Use concise, specific tags.
"""
        output = self.openai.generate_json(
            instructions=instructions.strip(),
            input_text=json.dumps(intake.model_dump(), ensure_ascii=False),
            schema=schema,
            name="coffee_member_profile",
        )
        data = extract_json_object(output)
        data["id"] = f"user_{uuid.uuid4().hex[:12]}"
        data["source"] = "user"
        data["search_text"] = profile_search_text(data)
        return MemberProfile(**data)

    def _create_profile_locally(self, intake: ProfileIntake) -> MemberProfile:
        data = {
            "id": f"user_{uuid.uuid4().hex[:12]}",
            "name": intake.name,
            "headline": intake.headline,
            "location": intake.location,
            "availability": intake.availability,
            "interests": split_terms(intake.interests),
            "expertise": split_terms(intake.expertise),
            "goals": split_terms(intake.goals),
            "current_need": intake.current_need,
            "preferred_formats": split_terms(intake.preferred_formats),
            "constraints": split_terms(intake.constraints),
            "profile_summary": self._local_summary(intake),
            "source": "user",
        }
        data["search_text"] = profile_search_text(data)
        return MemberProfile(**data)

    def _hydrate_seed_profile(self, raw_profile: dict) -> MemberProfile:
        data = dict(raw_profile)
        data["search_text"] = profile_search_text(data)
        return MemberProfile(**data)

    def _local_summary(self, intake: ProfileIntake) -> str:
        headline = intake.headline or "Community member"
        goal = intake.current_need or intake.goals or "looking for useful professional conversations"
        return f"{headline}. Currently {goal}."
