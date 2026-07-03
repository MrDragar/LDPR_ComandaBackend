from fastapi import Depends, Header, HTTPException, status
from src.core.containers import Container
from src.services.interfaces import IAuthService, IUserService, IPetitionService
from src.domain.entities.user import User
from src.domain.exceptions import AuthError, AuthBadUserError

__container = Container()


async def get_container() -> Container:
    return __container


async def get_auth_service(container: Container = Depends(get_container)) -> IAuthService:
    return container.auth_service()


async def get_user_service(container: Container = Depends(get_container)) -> IUserService:
    return container.user_service()


async def get_petition_service(container: Container = Depends(get_container)) -> IPetitionService:
    return container.petition_service()


async def get_current_user(authorization: str = Header(...), auth_service: IAuthService = Depends(get_auth_service)) -> User:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid auth scheme")
    token = authorization.split(" ")[1]
    try:
        user = await auth_service.get_user_by_token(token)
        return user
    except AuthBadUserError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    except AuthError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
