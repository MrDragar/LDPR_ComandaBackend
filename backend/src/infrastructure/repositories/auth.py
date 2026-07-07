import logging
from datetime import timedelta, datetime, UTC
from jose import jwt
from aiogram.utils.web_app import safe_parse_webapp_init_data

from src.domain.entities import Sources
from src.domain.exceptions import AuthError
from src.domain.interfaces import IJWTRepository, ITelegramAuthRepository, IVKAuthRepository, IMaxAuthRepository


class JWTRepository(IJWTRepository):
    def __init__(self, secret_key: str, algorithm: str):
        self.__secret_key = secret_key
        self.__algorithm = algorithm

    async def create_access_token(self, user_id: int, source: Sources, expires_delta: int | None = None) -> str:
        if expires_delta is None:
            expires_delta = 604800
        expire = datetime.now(UTC) + timedelta(seconds=expires_delta)
        data = {
            "id": user_id,
            "source": source.value,  # В JWT пишем строку
            "exp": int(expire.timestamp())
        }
        return jwt.encode(data, self.__secret_key, algorithm=self.__algorithm)

    async def decode_access_token(self, token: str) -> tuple[int, Sources]:
        try:
            payload = jwt.decode(token, self.__secret_key, algorithms=[self.__algorithm])
            if int(payload.get('exp')) < datetime.now(UTC).timestamp():
                raise AuthError('Токен истёк')
            if 'id' not in payload or 'source' not in payload:
                raise AuthError('Некорректный токен')
            return payload['id'], Sources(payload['source'])
        except jwt.JWTError:
            raise AuthError('Некорректный токен')


class TelegramAuthRepository(ITelegramAuthRepository):
    def __init__(self, token: str):
        self._token = token

    async def verify_data(self, auth_data: str) -> int:
        try:
            return int(auth_data)
            init_data = safe_parse_webapp_init_data(self._token, auth_data)
            if not init_data.user:
                raise AuthError("Нет данных пользователя")
            return init_data.user.id
        except ValueError:
            raise AuthError("Некорректные данные авторизации")
        except Exception as e:
            raise AuthError(f"Неизвестная ошибка {e}")


class VKAuthRepository(IVKAuthRepository):
    async def verify_data(self, auth_data: str) -> int:
        try:
            # В реальном приложении здесь должна быть проверка подписи от VK Bridge
            return int(auth_data)
        except ValueError:
            raise AuthError("Некорректные данные авторизации VK")


class MaxAuthRepository(IMaxAuthRepository):
    async def verify_data(self, auth_data: str) -> int:
        try:
            # В реальном приложении здесь должна быть проверка подписи от MAX
            return int(auth_data)
        except ValueError:
            raise AuthError("Некорректные данные авторизации MAX")
