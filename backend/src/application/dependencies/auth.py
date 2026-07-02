import logging

from fastapi import Header, Depends, HTTPException
from starlette import status

from src.application.dependencies.services import get_auth_service
from src.domain.entities import User
from src.domain.exceptions import AuthError
from src.services import AuthService


async def get_current_user(
        token: str = Header(..., alias="Authorization"),
        auth_service: AuthService = Depends(get_auth_service)
) -> User:
    if token.startswith("Bearer "):
        token = token[7:]
    try:
        user = await auth_service.get_user(token)
    except AuthError as e:
        logging.exception(e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Ошибка авторизации {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

