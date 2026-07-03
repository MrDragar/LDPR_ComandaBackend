from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from src.application.dependencies import get_current_user, get_stats_service
from src.domain.entities.user import User
from src.services.interfaces import IStatsService
from src.domain.exceptions import NotFoundRegionError

router = APIRouter()


class RegionCounterResponse(BaseModel):
    region: str
    count: int
    is_real: bool


class WeeklyReportResponse(BaseModel):
    period: dict
    petitions_created: int
    petitions_supported: int
    tasks_completed: int
    balance_earned: int
    impact_messages: List[str]


@router.get("/region-counter", response_model=RegionCounterResponse)
async def get_region_counter(user: User = Depends(get_current_user),
                             stats_service: IStatsService = Depends(get_stats_service)):
    if not user.region:
        raise HTTPException(status_code=400, detail={"error": "REGION_NOT_SET", "message": "У пользователя не указан регион"})
    try:
        return await stats_service.get_region_counter(user.region)
    except NotFoundRegionError:
        raise HTTPException(status_code=404, detail={"error": "REGION_NOT_FOUND", "message": "Регион не найден"})


@router.get("/weekly-report", response_model=WeeklyReportResponse)
async def get_weekly_report(user: User = Depends(get_current_user),
                            stats_service: IStatsService = Depends(get_stats_service)):
    return await stats_service.get_weekly_report(user.id, user.source.value)
