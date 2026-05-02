from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from threading import RLock
import uuid

from app.core.config import settings
from app.schemas.chat import (
    ChatMessage,
    ChatMessageCreate,
    ConversationCreate,
    ConversationDetail,
    ConversationSummary,
)


logger = logging.getLogger(__name__)


class ChatService:
    def __init__(self) -> None:
        self.store_path = Path(settings.chat_store_path)
        self._lock = RLock()

    def list_conversations(self, participant_id: str | None = None) -> list[ConversationSummary]:
        with self._lock:
            conversations = self._load()

        summaries = [self._to_summary(conversation) for conversation in conversations]
        if participant_id:
            summaries = [
                conversation
                for conversation in summaries
                if any(participant.id == participant_id for participant in conversation.participants)
            ]

        summaries.sort(key=lambda conversation: conversation.updated_at, reverse=True)
        logger.info(
            "chat.conversation.list participant_id=%s count=%s",
            participant_id or "all",
            len(summaries),
        )
        return summaries

    def create_conversation(self, request: ConversationCreate) -> ConversationDetail:
        with self._lock:
            conversations = self._load()
            existing = self._find_existing(conversations, request)
            if existing is not None:
                logger.info(
                    "chat.conversation.reuse conversation_id=%s participants=%s",
                    existing["id"],
                    [participant["id"] for participant in existing["participants"]],
                )
                return self._to_detail(existing)

            now = self._now()
            conversation = {
                "id": f"conv_{uuid.uuid4().hex[:12]}",
                "title": request.title or self._default_title(request),
                "participants": [
                    request.participant_a.model_dump(),
                    request.participant_b.model_dump(),
                ],
                "messages": [],
                "created_at": now,
                "updated_at": now,
            }
            conversations.append(conversation)
            self._save(conversations)

        logger.info(
            "chat.conversation.create conversation_id=%s participants=%s",
            conversation["id"],
            [participant["id"] for participant in conversation["participants"]],
        )
        return self._to_detail(conversation)

    def get_conversation(self, conversation_id: str) -> ConversationDetail | None:
        with self._lock:
            conversation = self._find_by_id(self._load(), conversation_id)

        if conversation is None:
            logger.info("chat.conversation.get conversation_id=%s found=false", conversation_id)
            return None

        logger.info(
            "chat.conversation.get conversation_id=%s found=true messages=%s",
            conversation_id,
            len(conversation["messages"]),
        )
        return self._to_detail(conversation)

    def add_message(self, conversation_id: str, request: ChatMessageCreate) -> ConversationDetail | None:
        with self._lock:
            conversations = self._load()
            conversation = self._find_by_id(conversations, conversation_id)
            if conversation is None:
                logger.info("chat.message.create conversation_id=%s found=false", conversation_id)
                return None

            now = self._now()
            message = {
                "id": f"msg_{uuid.uuid4().hex[:12]}",
                "conversation_id": conversation_id,
                "sender_id": request.sender_id,
                "sender_name": request.sender_name,
                "body": request.body.strip(),
                "created_at": now,
            }
            conversation["messages"].append(message)
            conversation["updated_at"] = now
            self._save(conversations)

        logger.info(
            "chat.message.create conversation_id=%s message_id=%s sender_id=%s body_chars=%s",
            conversation_id,
            message["id"],
            request.sender_id,
            len(request.body),
        )
        return self._to_detail(conversation)

    def _load(self) -> list[dict]:
        if not self.store_path.exists():
            return []
        with self.store_path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def _save(self, conversations: list[dict]) -> None:
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        with self.store_path.open("w", encoding="utf-8") as file:
            json.dump(conversations, file, ensure_ascii=False, indent=2)

    def _find_by_id(self, conversations: list[dict], conversation_id: str) -> dict | None:
        return next(
            (conversation for conversation in conversations if conversation["id"] == conversation_id),
            None,
        )

    def _find_existing(self, conversations: list[dict], request: ConversationCreate) -> dict | None:
        requested_ids = {request.participant_a.id, request.participant_b.id}
        for conversation in conversations:
            participant_ids = {participant["id"] for participant in conversation["participants"]}
            if participant_ids == requested_ids:
                return conversation
        return None

    def _to_summary(self, conversation: dict) -> ConversationSummary:
        messages = [ChatMessage(**message) for message in conversation["messages"]]
        return ConversationSummary(
            id=conversation["id"],
            title=conversation["title"],
            participants=conversation["participants"],
            created_at=conversation["created_at"],
            updated_at=conversation["updated_at"],
            last_message=messages[-1] if messages else None,
            message_count=len(messages),
        )

    def _to_detail(self, conversation: dict) -> ConversationDetail:
        summary = self._to_summary(conversation)
        return ConversationDetail(
            **summary.model_dump(),
            messages=[ChatMessage(**message) for message in conversation["messages"]],
        )

    def _default_title(self, request: ConversationCreate) -> str:
        return f"{request.participant_a.name} <> {request.participant_b.name}"

    def _now(self) -> str:
        return datetime.now(UTC).isoformat()
