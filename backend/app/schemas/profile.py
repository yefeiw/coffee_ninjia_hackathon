from pydantic import BaseModel, Field


class ProfileIntake(BaseModel):
    name: str = Field(..., min_length=1)
    headline: str = ""
    location: str = ""
    availability: str = ""
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
