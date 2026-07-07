from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from src.application.dependencies import get_current_user, get_cabinet_petition_service, get_cabinet_question_service, require_role
from src.domain.entities.user import User, UserRole
from src.services.interfaces import ICabinetPetitionService, ICabinetQuestionService
from src.domain.exceptions import CandidateNotAssignedError, PetitionNotAvailableError, QuestionNotFoundError

router = APIRouter()


# ==================== PETITIONS ====================
class CabinetPetitionItem(BaseModel):
    id: int
    title: str
    region: str
    support_count: int
    status: str
    created_at: str


class PaginatedCabinetPetitions(BaseModel):
    items: List[CabinetPetitionItem]
    page: int
    limit: int
    total: int


class TakePetitionRequest(BaseModel):
    initial_comment: str


class ProgressRequest(BaseModel):
    comment: str


class CompleteRequest(BaseModel):
    result: str
    result_image_url: Optional[str] = None


@router.get("/petitions", response_model=PaginatedCabinetPetitions)
async def get_cabinet_petitions(status: str = "available", page: int = 1, limit: int = 20,
                                user: User = Depends(require_role([UserRole.CANDIDATE, UserRole.STAFF_CA])),
                                service: ICabinetPetitionService = Depends(get_cabinet_petition_service)):
    try:
        return await service.get_petitions(user.id, user.source.value, status, page, limit)
    except CandidateNotAssignedError as e:
        raise HTTPException(status_code=403, detail={"error": "FORBIDDEN_ROLE", "message": str(e)})


@router.post("/petitions/{petition_id}/take")
async def take_petition(petition_id: int, data: TakePetitionRequest,
                        user: User = Depends(require_role([UserRole.CANDIDATE, UserRole.STAFF_CA])),
                        service: ICabinetPetitionService = Depends(get_cabinet_petition_service)):
    try:
        return await service.take_petition(user.id, user.source.value, petition_id, data.initial_comment)
    except CandidateNotAssignedError as e:
        raise HTTPException(status_code=403, detail={"error": "FORBIDDEN_ROLE", "message": str(e)})
    except PetitionNotAvailableError as e:
        raise HTTPException(status_code=409, detail={"error": "PETITION_ALREADY_TAKEN", "message": str(e)})


@router.post("/petitions/{petition_id}/progress")
async def update_progress(petition_id: int, data: ProgressRequest,
                          user: User = Depends(require_role([UserRole.CANDIDATE, UserRole.STAFF_CA])),
                          service: ICabinetPetitionService = Depends(get_cabinet_petition_service)):
    try:
        return await service.update_progress(user.id, user.source.value, petition_id, data.comment)
    except CandidateNotAssignedError as e:
        raise HTTPException(status_code=403, detail={"error": "FORBIDDEN_ROLE", "message": str(e)})


@router.post("/petitions/{petition_id}/complete")
async def complete_petition(petition_id: int, data: CompleteRequest,
                            user: User = Depends(require_role([UserRole.CANDIDATE, UserRole.STAFF_CA])),
                            service: ICabinetPetitionService = Depends(get_cabinet_petition_service)):
    try:
        return await service.complete_petition(user.id, user.source.value, petition_id, data.result, data.result_image_url)
    except CandidateNotAssignedError as e:
        raise HTTPException(status_code=403, detail={"error": "FORBIDDEN_ROLE", "message": str(e)})


# ==================== QUESTIONS ====================
class QuestionItem(BaseModel):
    id: int
    text: str
    is_anonymous: bool
    author_name: str
    status: str
    created_at: str


class PaginatedQuestions(BaseModel):
    items: List[QuestionItem]
    page: int
    limit: int
    total: int


class AnswerRequest(BaseModel):
    text: Optional[str] = None
    voice_url: Optional[str] = None
    video_url: Optional[str] = None


@router.get("/questions", response_model=PaginatedQuestions)
async def get_cabinet_questions(status: Optional[str] = None, page: int = 1, limit: int = 20,
                                user: User = Depends(require_role([UserRole.CANDIDATE, UserRole.STAFF_CA])),
                                service: ICabinetQuestionService = Depends(get_cabinet_question_service)):
    try:
        return await service.get_questions(user.id, user.source.value, status, page, limit)
    except CandidateNotAssignedError as e:
        raise HTTPException(status_code=403, detail={"error": "FORBIDDEN_ROLE", "message": str(e)})


@router.post("/questions/{question_id}/answer")
async def answer_question(question_id: int, data: AnswerRequest,
                          user: User = Depends(require_role([UserRole.CANDIDATE, UserRole.STAFF_CA])),
                          service: ICabinetQuestionService = Depends(get_cabinet_question_service)):
    try:
        return await service.answer_question(user.id, user.source.value, question_id, data.text, data.voice_url, data.video_url)
    except QuestionNotFoundError as e:
        raise HTTPException(status_code=404, detail={"error": "QUESTION_NOT_FOUND", "message": str(e)})
    except CandidateNotAssignedError as e:
        raise HTTPException(status_code=403, detail={"error": "FORBIDDEN_ROLE", "message": str(e)})
