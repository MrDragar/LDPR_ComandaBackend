from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.application.dependencies import get_admin_petition_service, require_role
from src.domain.entities.user import User, UserRole
from src.services.interfaces import IAdminPetitionService
from src.domain.exceptions import PetitionError, PetitionAlreadyModeratedError

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
