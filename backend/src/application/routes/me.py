from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from src.application.dependencies import get_current_user, get_auth_service
from src.domain.entities.user import User, Sources
from src.services.interfaces import IAuthService

router = APIRouter()


class MeResponse(BaseModel):
    id: int
    source: Sources
    username: Optional[str]
    surname: str
    name: Optional[str]
    patronymic: Optional[str]
    phone_number: str
    birth_date: Optional[str]
    region: Optional[str]
    email: Optional[str]
    gender: Optional[str]
    city: Optional[str]
    wish_to_join: Optional[bool]
    home_address: Optional[str]
    news_subscription: bool
    created_at: str
    balance: int
    role: str
    grade: str


class PatchMeRequest(BaseModel):
    username: Optional[str] = None
    surname: Optional[str] = None
    name: Optional[str] = None
    patronymic: Optional[str] = None
    phone_number: Optional[str] = None
    birth_date: Optional[date] = None
    region: Optional[str] = None
    email: Optional[str] = None
    gender: Optional[str] = None
    city: Optional[str] = None
    wish_to_join: Optional[bool] = None
    home_address: Optional[str] = None
    news_subscription: Optional[bool] = None


@router.get("/me", response_model=MeResponse)
async def get_me(user: User = Depends(get_current_user)):
    return MeResponse(
        id=user.id, source=user.source.value, username=user.username, surname=user.surname,
        name=user.name, patronymic=user.patronymic, phone_number=user.phone_number,
        birth_date=user.birth_date.isoformat() if user.birth_date else None,
        region=user.region, email=user.email, gender=user.gender, city=user.city,
        wish_to_join=user.wish_to_join, home_address=user.home_address,
        news_subscription=user.news_subscription, created_at=user.created_at.isoformat(),
        balance=user.balance, role=user.role.value, grade=user.grade.value
    )


@router.patch("/me", response_model=MeResponse)
async def patch_me(data: PatchMeRequest, user: User = Depends(get_current_user),
                   auth_service: IAuthService = Depends(get_auth_service)):
    updates = {k: v for k, v in data.dict().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400,
                            detail={"error": "INVALID_PAYLOAD", "message": "No fields to update"})

    updated_user = await auth_service.update_user_profile(user.id, user.source, **updates)
    return MeResponse(
        id=updated_user.id, source=updated_user.source.value, username=updated_user.username,
        surname=updated_user.surname,
        name=updated_user.name, patronymic=updated_user.patronymic,
        phone_number=updated_user.phone_number,
        birth_date=updated_user.birth_date.isoformat() if updated_user.birth_date else None,
        region=updated_user.region, email=updated_user.email, gender=updated_user.gender,
        city=updated_user.city,
        wish_to_join=updated_user.wish_to_join, home_address=updated_user.home_address,
        news_subscription=updated_user.news_subscription,
        created_at=updated_user.created_at.isoformat(),
        balance=updated_user.balance, role=updated_user.role.value, grade=updated_user.grade.value
    )
