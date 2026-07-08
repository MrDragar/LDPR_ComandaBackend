from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.application.dependencies import get_current_user, get_hill_service
from src.domain.entities.user import User
from src.services.interfaces import IHillService
from src.domain.exceptions import HillError

router = APIRouter()


class PetitionCard(BaseModel):
    id: int
    title: str
    description: str
    region: str
    support_count: int
    image_url: str | None


class BattleResponse(BaseModel):
    left: PetitionCard
    right: PetitionCard


class ChoiceRequest(BaseModel):
    left_id: int
    right_id: int
    winner_id: int


class StatsResponse(BaseModel):
    total_votes: int


@router.get("/battle", response_model=BattleResponse)
async def get_battle(user: User = Depends(get_current_user),
                     hill_service: IHillService = Depends(get_hill_service)):
    result = await hill_service.get_battle(user.id, user.source)
    if result.get("status") == "no_petitions":
        raise HTTPException(status_code=404, detail={"error": "NO_PETITIONS", "message": result["message"]})
    return result


@router.post("/choice")
async def make_choice(data: ChoiceRequest, user: User = Depends(get_current_user),
                      hill_service: IHillService = Depends(get_hill_service)):
    try:
        return await hill_service.make_choice(user.id, user.source, data.left_id, data.right_id, data.winner_id)
    except HillError as e:
        raise HTTPException(status_code=400, detail={"error": "INVALID_CHOICE", "message": str(e)})


@router.get("/stats", response_model=StatsResponse)
async def get_stats(user: User = Depends(get_current_user),
                    hill_service: IHillService = Depends(get_hill_service)):
    return await hill_service.get_stats(user.id, user.source)
