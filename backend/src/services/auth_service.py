import logging
from src.domain.entities.user import User, Sources
from src.domain.exceptions import AuthError, AuthBadUserError, UserNotFoundError
from src.domain.interfaces import IUserRepository, IJWTRepository, ITelegramAuthRepository, IVKAuthRepository, IMaxAuthRepository, IUnitOfWork
from src.services.interfaces import IAuthService

logger = logging.getLogger(__name__)

class AuthService(IAuthService):
    def __init__(self, user_repo: IUserRepository, jwt_repo: IJWTRepository,
                 tg_auth_repo: ITelegramAuthRepository, vk_auth_repo: IVKAuthRepository,
                 max_auth_repo: IMaxAuthRepository, uow: IUnitOfWork):
        self.__user_repo = user_repo
        self.__jwt_repo = jwt_repo
        self.__tg_auth_repo = tg_auth_repo
        self.__vk_auth_repo = vk_auth_repo
        self.__max_auth_repo = max_auth_repo
        self.__uow = uow

    async def authenticate_tg(self, auth_data: str) -> str:
        user_id = await self.__tg_auth_repo.verify_data(auth_data)
        return await self.__generate_token(user_id, Sources.TG.value)

    async def authenticate_vk(self, auth_data: str) -> str:
        user_id = await self.__vk_auth_repo.verify_data(auth_data)
        return await self.__generate_token(user_id, Sources.VK.value)

    async def authenticate_max(self, auth_data: str) -> str:
        user_id = await self.__max_auth_repo.verify_data(auth_data)
        return await self.__generate_token(user_id, Sources.MAX.value)

    async def __generate_token(self, user_id: int, source: Sources) -> str:
        async with self.__uow.atomic():
            try:
                user = await self.__user_repo.get_user(user_id, source)
            except UserNotFoundError:
                raise AuthBadUserError("Пользователь не найден. Пройдите регистрацию в боте.")
            except Exception as e:
                logger.error(f"Auth error: {e}")
                raise AuthError("Ошибка авторизации")
        return await self.__jwt_repo.create_access_token(user_id, source)

    async def get_user_by_token(self, token: str) -> User:
        try:
            user_id, source_str = await self.__jwt_repo.decode_access_token(token)
            source = source_str
            async with self.__uow.atomic():
                user = await self.__user_repo.get_user(user_id, source)
            return user
        except AuthError:
            raise
        except UserNotFoundError:
            raise AuthBadUserError("Пользователь не найден")
        except Exception as e:
            logger.error(f"Token decode error: {e}")
            raise AuthError("Некорректный токен")

    async def update_user_profile(self, user_id: int, source: Sources, **kwargs) -> User:
        async with self.__uow.atomic():
            return await self.__user_repo.update_user_profile(user_id, source, **kwargs)
        