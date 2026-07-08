from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.application.dependencies import get_auth_service
from src.services.interfaces import IAuthService
from src.domain.exceptions import AuthError, AuthBadUserError, UserAlreadyExistsError

router = APIRouter()


class AuthResponse(BaseModel):
    access_token: str
    expires_in: int = 604800


class RegisterRequest(BaseModel):
    auth_data: str
    source: str
    surname: str
    name: Optional[str] = None
    patronymic: Optional[str] = None
    phone_number: str
    birth_date: Optional[str] = None
    region: Optional[str] = None
    email: Optional[str] = None
    gender: Optional[str] = None
    city: Optional[str] = None
    wish_to_join: Optional[bool] = False
    home_address: Optional[str] = None
    news_subscription: bool = False
    is_member: Optional[bool] = None
    username: Optional[str] = None


@router.post("/register", response_model=AuthResponse)
async def register(data: RegisterRequest, auth_service: IAuthService = Depends(get_auth_service)):
    try:
        user_data = data.dict(exclude={"auth_data", "source"})
        token = await auth_service.register(data.auth_data, data.source, user_data)
        return {"access_token": token}
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail={"error": "USER_ALREADY_EXISTS", "message": str(e)})
    except AuthError as e:
        raise HTTPException(status_code=400, detail={"error": "INVALID_PAYLOAD", "message": str(e)})


@router.post("/tg", response_model=AuthResponse)
async def auth_tg(data: dict, auth_service: IAuthService = Depends(get_auth_service)):
    auth_data = data.get("init_data") or data.get("auth_data")
    if not auth_data:
        raise HTTPException(status_code=400, detail={"error": "INVALID_PAYLOAD", "message": "Missing auth_data"})
    try:
        token = await auth_service.authenticate_tg(auth_data)
        return {"access_token": token}
    except AuthBadUserError as e:
        raise HTTPException(status_code=401, detail={"error": "UNAUTHORIZED", "message": str(e)})
    except AuthError as e:
        raise HTTPException(status_code=400, detail={"error": "INVALID_PAYLOAD", "message": str(e)})


@router.post("/vk", response_model=AuthResponse)
async def auth_vk(data: dict, auth_service: IAuthService = Depends(get_auth_service)):
    auth_data = data.get("auth_data") or data.get("vk_user_id")
    if not auth_data:
        raise HTTPException(status_code=400, detail={"error": "INVALID_PAYLOAD", "message": "Missing auth_data"})
    try:
        token = await auth_service.authenticate_vk(str(auth_data))
        return {"access_token": token}
    except AuthBadUserError as e:
        raise HTTPException(status_code=401, detail={"error": "UNAUTHORIZED", "message": str(e)})
    except AuthError as e:
        raise HTTPException(status_code=400, detail={"error": "INVALID_PAYLOAD", "message": str(e)})


@router.post("/max", response_model=AuthResponse)
async def auth_max(data: dict, auth_service: IAuthService = Depends(get_auth_service)):
    auth_data = data.get("auth_data") or data.get("max_user_id")
    if not auth_data:
        raise HTTPException(status_code=400, detail={"error": "INVALID_PAYLOAD", "message": "Missing auth_data"})
    try:
        token = await auth_service.authenticate_max(str(auth_data))
        return {"access_token": token}
    except AuthBadUserError as e:
        raise HTTPException(status_code=401, detail={"error": "UNAUTHORIZED", "message": str(e)})
    except AuthError as e:
        raise HTTPException(status_code=400, detail={"error": "INVALID_PAYLOAD", "message": str(e)})
