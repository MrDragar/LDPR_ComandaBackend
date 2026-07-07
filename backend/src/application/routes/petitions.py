from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from src.application.dependencies import get_current_user, get_petition_service
from src.domain.entities.user import User, UserRole
from src.services.interfaces import IPetitionService
from src.domain.exceptions import PetitionError

router = APIRouter()


class PetitionResponse(BaseModel):
    id: int
    title: str
    description: str
    region: str
    scope: str
    image_url: Optional[str]
    author_id: int
    author_name: str
    support_count: int
    share_count: int
    view_count: int
    status: str
    candidate_id: Optional[int]
    candidate_name: Optional[str]
    candidate_progress: Optional[str]
    candidate_result: Optional[str]
    is_supported_by_me: bool
    created_at: str


class CreatePetitionRequest(BaseModel):
    title: str
    description: str
    image_url: Optional[str] = None
    scope: str


class SupportResponse(BaseModel):
    support_count: int
    reward: int = 2


class ShareResponse(BaseModel):
    share_url_vk: str
    share_url_tg: str
    share_url_max: str

class PaginatedPetitions(BaseModel):
    items: List[PetitionResponse]
    page: int
    limit: int
    total: int


@router.get("/feed", response_model=List[PetitionResponse])
async def get_feed(scope: Optional[str] = None, region: Optional[str] = None, limit: int = 20,
                   user: User = Depends(get_current_user),
                   petition_service: IPetitionService = Depends(get_petition_service)):
    return await petition_service.get_feed(user.id, user.source.value, scope, region, limit)


@router.post("", status_code=201)
async def create_petition(data: CreatePetitionRequest, user: User = Depends(get_current_user),
                          petition_service: IPetitionService = Depends(get_petition_service)):
    if data.scope == "federal" and user.role != UserRole.STAFF_CA:
        raise HTTPException(status_code=403, detail={"error": "FORBIDDEN_ROLE", "message": "Only STAFF_CA can create federal petitions"})
    try:
        petition = await petition_service.create_petition(user.id, user.source.value, data.title, data.description, data.image_url, data.scope)
        return {"id": petition.id, "status": petition.status.value, "message": "Петиция отправлена на модерацию"}
    except PetitionError as e:
        raise HTTPException(status_code=400, detail={"error": "INVALID_PAYLOAD", "message": str(e)})


@router.get("/{petition_id}", response_model=PetitionResponse)
async def get_petition(petition_id: int, user: User = Depends(get_current_user),
                       petition_service: IPetitionService = Depends(get_petition_service)):
    try:
        return await petition_service.get_petition(petition_id, user.id, user.source.value)
    except PetitionError as e:
        raise HTTPException(status_code=404, detail={"error": "PETITION_NOT_FOUND", "message": str(e)})


@router.post("/{petition_id}/support", response_model=SupportResponse)
async def support_petition(petition_id: int, user: User = Depends(get_current_user),
                           petition_service: IPetitionService = Depends(get_petition_service)):
    try:
        count = await petition_service.support_petition(petition_id, user.id, user.source.value)
        return {"support_count": count, "reward": 2}
    except PetitionError as e:
        if "уже поддержали" in str(e):
            raise HTTPException(status_code=409, detail={"error": "PETITION_ALREADY_SUPPORTED", "message": str(e)})
        raise HTTPException(status_code=400, detail={"error": "PETITION_UNDER_MODERATION", "message": str(e)})


@router.post("/{petition_id}/skip")
async def skip_petition(petition_id: int, user: User = Depends(get_current_user),
                        petition_service: IPetitionService = Depends(get_petition_service)):
    return await petition_service.skip_petition(petition_id, user.id, user.source.value)


@router.post("/{petition_id}/share", response_model=ShareResponse)
async def share_petition(petition_id: int, user: User = Depends(get_current_user),
                         petition_service: IPetitionService = Depends(get_petition_service)):
    return await petition_service.share_petition(petition_id)


@router.get("", response_model=PaginatedPetitions)
async def get_petitions(scope: Optional[str] = None, status: Optional[str] = None, region: Optional[str] = None,
                        page: int = 1, limit: int = 20, user: User = Depends(get_current_user),
                        petition_service: IPetitionService = Depends(get_petition_service)):
    return await petition_service.get_all(scope, status, region, page, limit)


@router.get("/my", response_model=PaginatedPetitions)
async def get_my_petitions(page: int = 1, limit: int = 20, user: User = Depends(get_current_user),
                           petition_service: IPetitionService = Depends(get_petition_service)):
    return await petition_service.get_my(user.id, user.source.value, page, limit)


@router.get("/supported", response_model=PaginatedPetitions)
async def get_supported_petitions(page: int = 1, limit: int = 20, user: User = Depends(get_current_user),
                                  petition_service: IPetitionService = Depends(get_petition_service)):
    return await petition_service.get_supported(user.id, user.source.value, page, limit)
