import logging
from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException

from src.application.dependencies.auth import get_current_user
from src.application.dependencies.services import get_auth_service
from src.application.schema.auth import TelegramAuthData, JWTToken, MeResponse
from src.domain.entities import User
from src.services.interfaces import IAuthService

router = APIRouter(prefix="/auth")


@router.post('/login', response_model=JWTToken)
async def login(
        auth_data: TelegramAuthData,
        auth_service: IAuthService = Depends(get_auth_service)
):
    try:
        token = await auth_service.authenticate(auth_data.initData)
    except Exception as e:
        logging.exception(e)
        raise HTTPException(status_code=401, detail=f"{e}")
    return {
        'token': token
    }


@router.get('/me', response_model=MeResponse)
async def me(
        user: User = Depends(get_current_user)
):
    return asdict(user)
