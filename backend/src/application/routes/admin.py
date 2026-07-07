from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.application.dependencies import get_admin_petition_service, require_role, \
    get_admin_candidate_service
from src.domain.entities.user import User, UserRole
from src.services.interfaces import IAdminPetitionService, IAdminCandidateService
from src.domain.exceptions import PetitionError, PetitionAlreadyModeratedError, UserNotFoundError, \
    CandidateAlreadyExistsError

router = APIRouter()


class RejectRequest(BaseModel):
    reason: str


class ModerationResponse(BaseModel):
    status: str
    message: str


@router.post("/petitions/{petition_id}/approve", response_model=ModerationResponse)
async def approve_petition(petition_id: int, 
                           user: User = Depends(require_role([UserRole.STAFF_CA])),
                           admin_service: IAdminPetitionService = Depends(get_admin_petition_service)):
    try:
        return await admin_service.approve_petition(petition_id)
    except PetitionError:
        raise HTTPException(status_code=404, detail={"error": "PETITION_NOT_FOUND", "message": "Петиция не найдена"})
    except PetitionAlreadyModeratedError:
        raise HTTPException(status_code=400, detail={"error": "PETITION_ALREADY_MODERATED", "message": "Петиция уже модерирована"})


@router.post("/petitions/{petition_id}/reject", response_model=ModerationResponse)
async def reject_petition(petition_id: int, data: RejectRequest,
                          user: User = Depends(require_role([UserRole.STAFF_CA])),
                          admin_service: IAdminPetitionService = Depends(get_admin_petition_service)):
    if not data.reason.strip():
        raise HTTPException(status_code=400, detail={"error": "INVALID_PAYLOAD", "message": "Причина отклонения обязательна"})
    try:
        return await admin_service.reject_petition(petition_id, data.reason)
    except PetitionError:
        raise HTTPException(status_code=404, detail={"error": "PETITION_NOT_FOUND", "message": "Петиция не найдена"})
    except PetitionAlreadyModeratedError:
        raise HTTPException(status_code=400, detail={"error": "PETITION_ALREADY_MODERATED", "message": "Петиция уже модерирована"})


class CreateCandidateRequest(BaseModel):
    user_id: int
    source: str
    fio: str
    region: str
    photo_url: Optional[str] = None
    bio: Optional[str] = None
    topics: List[str] = []
    social_links: dict = {}


class CreateCandidateResponse(BaseModel):
    candidate_id: int
    message: str


@router.post("/candidates", status_code=201, response_model=CreateCandidateResponse)
async def create_candidate(data: CreateCandidateRequest,
                           user: User = Depends(require_role([UserRole.STAFF_CA])),
                           admin_service: IAdminCandidateService = Depends(get_admin_candidate_service)):
    try:
        return await admin_service.create_candidate(
            data.user_id, data.source, data.fio, data.region, data.photo_url, 
            data.bio, data.topics, data.social_links
        )
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail={"error": "USER_NOT_FOUND", "message": "Пользователь не найден"})
    except CandidateAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail={"error": "CANDIDATE_ALREADY_EXISTS", "message": str(e)})
