from fastapi import Depends

from src.core.containers import Container
from src.services.interfaces import IAuthService, IUserService

__container = Container()


async def get_container() -> Container:
    return __container


async def get_auth_service(container: Container = Depends(get_container)) -> IAuthService:
    return container.auth_service()


async def get_user_service(container: Container = Depends(get_container)) -> IUserService:
    return container.user_service()
