from enum import Enum

from pydantic import BaseModel, Field


class ConversationStyle(str, Enum):
    tactical = "tactical"
    strategic = "strategic"
    casual = "casual"


class ProfileIntake(BaseModel):
    name: str = Field(..., min_length=1)
    headline: str = ""
    location: str = ""
    availability: str = ""
    can_help_with: str = ""
    want_help_with: str = ""
    company: str = ""
    level: str = ""
    years: str = ""
    years_experience: int | None = None
    conversation_style: ConversationStyle | None = None
    interests: str = ""
    expertise: str = ""
    goals: str = ""
    current_need: str = ""
    preferred_formats: str = ""
    constraints: str = ""


class MemberProfile(BaseModel):
    id: str
    name: str
    headline: str
    location: str
    availability: str
    can_help_with: list[str] = Field(default_factory=list)
    want_help_with: list[str] = Field(default_factory=list)
    company: str = ""
    level: str = ""
    years: str = ""
    years_experience: int | None = None
    conversation_style: ConversationStyle | None = None
    interests: list[str]
    expertise: list[str]
    goals: list[str]
    current_need: str
    preferred_formats: list[str]
    constraints: list[str]
    profile_summary: str
    search_text: str
    source: str = "user"


class ProfileResponse(BaseModel):
    profile: MemberProfile
    used_llm: bool
