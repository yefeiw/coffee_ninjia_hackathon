from fastapi import APIRouter

from app.schemas.match import MatchRequest, MatchResponse
from app.schemas.profile import ProfileIntake, ProfileResponse
from app.services.matching_service import MatchingService
from app.services.profile_service import ProfileService


router = APIRouter(prefix="/api", tags=["coffee"])
profile_service = ProfileService()
matching_service = MatchingService(profile_service)


@router.post("/onboarding", response_model=ProfileResponse)
def onboard_member(intake: ProfileIntake) -> ProfileResponse:
    profile, used_llm = profile_service.create_profile(intake)
    return ProfileResponse(profile=profile, used_llm=used_llm)


@router.post("/matches", response_model=MatchResponse)
def generate_matches(request: MatchRequest) -> MatchResponse:
    response = matching_service.match(profile=request.profile, need=request.need)
    return response


@router.post("/seed")
def seed_profiles() -> dict:
    profile_service.seed_profiles()
    return {"status": "ok"}
