import logging

from fastapi import APIRouter, HTTPException, Query

from app.schemas.chat import ChatMessageCreate, ConversationCreate, ConversationDetail, ConversationSummary
from app.schemas.match import MatchRequest, MatchResponse
from app.schemas.profile import ProfileIntake, ProfileResponse
from app.services.chat_service import ChatService
from app.services.matching_service import MatchingService
from app.services.profile_service import ProfileService


router = APIRouter(prefix="/api", tags=["coffee"])
logger = logging.getLogger(__name__)
profile_service = ProfileService()
matching_service = MatchingService(profile_service)
chat_service = ChatService()


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


@router.get("/admin/profiles")
def list_all_profiles() -> list[dict]:
    return profile_service.vector_store.list_all()


@router.get("/conversations", response_model=list[ConversationSummary])
def list_conversations(participant_id: str | None = Query(default=None)) -> list[ConversationSummary]:
    return chat_service.list_conversations(participant_id=participant_id)


@router.post("/conversations", response_model=ConversationDetail)
def create_conversation(request: ConversationCreate) -> ConversationDetail:
    return chat_service.create_conversation(request)


@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
def get_conversation(conversation_id: str) -> ConversationDetail:
    conversation = chat_service.get_conversation(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@router.post("/conversations/{conversation_id}/messages", response_model=ConversationDetail)
def add_message(conversation_id: str, request: ChatMessageCreate) -> ConversationDetail:
    conversation = chat_service.add_message(conversation_id, request)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation
