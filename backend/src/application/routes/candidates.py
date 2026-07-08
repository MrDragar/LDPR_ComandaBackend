from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from src.application.dependencies import get_current_user, get_candidate_service
from src.domain.entities.user import User
from src.services.interfaces import ICandidateService
from src.domain.exceptions import CandidateNotFoundError

router = APIRouter()


class CandidateListItem(BaseModel):
    id: int
    fio: str
    region: str
    photo_url: Optional[str]
    topics: List[str]
    petitions_in_progress: int
    petitions_completed: int


class CandidateDetail(BaseModel):
    id: int
    fio: str
    region: str
    photo_url: Optional[str]
    bio: Optional[str]
    topics: List[str]
    social_links: dict
    petitions_in_progress: List[dict]
    petitions_completed: List[dict]


class PaginatedCandidates(BaseModel):
    items: List[CandidateListItem]
    page: int
    limit: int
    total: int


class QuestionRequest(BaseModel):
    text: str
    is_anonymous: bool = False


class QuestionResponse(BaseModel):
    question_id: int
    status: str


class MyQuestionItem(BaseModel):
    id: int
    candidate_id: int
    text: str
    status: str
    created_at: str
    answer_text: Optional[str] = None
    answer_voice_url: Optional[str] = None
    answer_video_url: Optional[str] = None


class PaginatedMyQuestions(BaseModel):
    items: List[MyQuestionItem]
    page: int
    limit: int
    total: int


@router.get("/questions/my", response_model=PaginatedMyQuestions)
async def get_my_questions(page: int = 1, limit: int = 20,
                           user: User = Depends(get_current_user),
                           candidate_service: ICandidateService = Depends(get_candidate_service)):
    return await candidate_service.get_my_questions(user.id, user.source, page, limit)


@router.get("", response_model=PaginatedCandidates)
async def get_candidates(region: Optional[str] = None, page: int = 1, limit: int = 20,
                         user: User = Depends(get_current_user),
                         candidate_service: ICandidateService = Depends(get_candidate_service)):
    return await candidate_service.get_candidates(region, page, limit)


@router.get("/{candidate_id}", response_model=CandidateDetail)
async def get_candidate(candidate_id: int, user: User = Depends(get_current_user),
                        candidate_service: ICandidateService = Depends(get_candidate_service)):
    try:
        return await candidate_service.get_candidate_by_id(candidate_id)
    except CandidateNotFoundError:
        raise HTTPException(status_code=404, detail={"error": "CANDIDATE_NOT_FOUND", "message": "Кандидат не найден"})


@router.post("/{candidate_id}/questions", status_code=201, response_model=QuestionResponse)
async def ask_question(candidate_id: int, data: QuestionRequest, user: User = Depends(get_current_user),
                       candidate_service: ICandidateService = Depends(get_candidate_service)):
    if not data.text.strip():
        raise HTTPException(status_code=400, detail={"error": "INVALID_PAYLOAD", "message": "Текст вопроса не может быть пустым"})
    try:
        return await candidate_service.ask_question(candidate_id, user.id, user.source, data.text, data.is_anonymous)
    except CandidateNotFoundError:
        raise HTTPException(status_code=404, detail={"error": "CANDIDATE_NOT_FOUND", "message": "Кандидат не найден"})
