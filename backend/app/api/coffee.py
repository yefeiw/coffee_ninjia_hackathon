import logging

from fastapi import APIRouter

from app.schemas.match import MatchRequest, MatchResponse
from app.schemas.profile import ProfileIntake, ProfileResponse
from app.services.matching_service import MatchingService
from app.services.profile_service import ProfileService


router = APIRouter(prefix="/api", tags=["coffee"])
logger = logging.getLogger(__name__)
profile_service = ProfileService()
matching_service = MatchingService(profile_service)


@router.post("/onboarding", response_model=ProfileResponse)
def onboard_member(intake: ProfileIntake) -> ProfileResponse:
    logger.info("onboarding.request name=%s location=%s", intake.name, intake.location)
    profile, used_llm = profile_service.create_profile(intake)
    logger.info(
        "onboarding.response profile_id=%s used_llm=%s interests=%s expertise=%s",
        profile.id,
        used_llm,
        len(profile.interests),
        len(profile.expertise),
    )
    return ProfileResponse(profile=profile, used_llm=used_llm)


@router.post("/matches", response_model=MatchResponse)
def generate_matches(request: MatchRequest) -> MatchResponse:
    logger.info(
        "matching.request profile_id=%s profile_name=%s need_chars=%s",
        request.profile.id,
        request.profile.name,
        len(request.need),
    )
    response = matching_service.match(profile=request.profile, need=request.need)
    logger.info(
        "matching.response profile_id=%s matches=%s used_llm=%s",
        request.profile.id,
        len(response.matches),
        response.used_llm,
    )
    return response


@router.post("/seed")
def seed_profiles() -> dict:
    profile_service.seed_profiles()
    return {"status": "ok"}
