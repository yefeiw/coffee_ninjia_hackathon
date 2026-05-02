from datetime import datetime

from pydantic import BaseModel, Field


class ChatParticipant(BaseModel):
    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    headline: str = ""


class ChatMessage(BaseModel):
    id: str
    conversation_id: str
    sender_id: str
    sender_name: str
    body: str
    created_at: datetime


class ConversationCreate(BaseModel):
    participant_a: ChatParticipant
    participant_b: ChatParticipant
    title: str = ""


class ChatMessageCreate(BaseModel):
    sender_id: str = Field(..., min_length=1)
    sender_name: str = Field(..., min_length=1)
    body: str = Field(..., min_length=1)


class ConversationSummary(BaseModel):
    id: str
    title: str
    participants: list[ChatParticipant]
    created_at: datetime
    updated_at: datetime
    last_message: ChatMessage | None = None
    message_count: int


class ConversationDetail(ConversationSummary):
    messages: list[ChatMessage]
