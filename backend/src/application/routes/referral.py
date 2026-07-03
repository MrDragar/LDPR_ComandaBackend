from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.application.dependencies import get_current_user
from src.domain.entities.user import User
from src.core.containers import Container
from src.services.interfaces import IReferralLinkService, IReferralService

router = APIRouter()


class ReferralLinkResponse(BaseModel):
    vk: str
    tg: str
    max: str
    invitees_count: int


@router.get("/link", response_model=ReferralLinkResponse)
async def get_referral_link(user: User = Depends(get_current_user)):
    container = Container()
    referral_link_service: IReferralLinkService = container.referral_link_service()
    referral_service: IReferralService = container.referral_service()

    invitees_count = await referral_service.get_count_invitees(user.id, user.source)

    return {
        "vk": f"{referral_link_service.vk_bot_link}?ref={user.id}_{user.source.value}",
        "tg": f"{referral_link_service.tg_bot_link}?start={user.id}_{user.source.value}",
        "max": f"{referral_link_service.max_bot_link}?start={user.id}_{user.source.value}",
        "invitees_count": invitees_count
    }
