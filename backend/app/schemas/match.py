from pydantic import BaseModel, Field

from app.schemas.profile import MemberProfile


class MatchRequest(BaseModel):
    profile: MemberProfile
    need: str = Field(..., min_length=1)


class CandidateMatch(BaseModel):
    candidate_id: str
    candidate_name: str
    candidate_headline: str
    score: float
    match_type: str
    you_want: str = ""
    they_did: str = ""
    they_want: str = ""
    you_have: str = ""
    why_now: str
    why_this_matters: str = ""
    evidence: list[str]
    suggested_activity: str
    conversation_starters: list[str]
    risks: list[str]
    next_step_message: str


class MatchResponse(BaseModel):
    query_summary: str
    matches: list[CandidateMatch]
    used_llm: bool
