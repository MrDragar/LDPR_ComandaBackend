import logging
from datetime import timedelta, datetime, UTC
import base64
import hashlib
import hmac
import json
from operator import itemgetter
from urllib.parse import parse_qsl, urlencode
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
            # aiogram сам проверяет hash и парсит данные Mini App
            init_data = safe_parse_webapp_init_data(self._token, auth_data)
            if not init_data.user:
                raise AuthError("Нет данных пользователя")
            return init_data.user.id
        except ValueError:
            raise AuthError("Некорректные данные авторизации Telegram")
        except Exception as e:
            raise AuthError(f"Ошибка авторизации Telegram: {e}")


class MAXAuthRepository(IMaxAuthRepository):
    def __init__(self, bot_token: str):
        self._bot_token = bot_token

    async def verify_data(self, auth_data: str) -> int:
        try:
            # 1. Парсим строку и декодируем URL-символы
            params = list(dict(parse_qsl(auth_data, keep_blank_values=True)).items())

            # 2. Ищем hash и user
            original_hash = next((v for k, v in params if k == 'hash'), None)
            user_str = next((v for k, v in params if k == 'user'), None)

            if not original_hash or not user_str:
                raise AuthError("Отсутствуют обязательные параметры (hash/user)")

            # 3. Сортируем параметры по ключу (a -> z), исключая hash
            params_to_sign = sorted([(k, v) for k, v in params if k != 'hash'], key=itemgetter(0))

            # 4. Формируем строку launch_params через \n
            launch_params = '\n'.join(f'{k}={v}' for k, v in params_to_sign)

            # 5. Создаем secret_key
            secret_key = hmac.new(
                key=b"WebAppData",
                msg=self._bot_token.encode('utf-8'),
                digestmod=hashlib.sha256
            ).digest()

            # 6. Вычисляем проверочный hash
            calculated_hash = hmac.new(
                key=secret_key,
                msg=launch_params.encode('utf-8'),
                digestmod=hashlib.sha256
            ).hexdigest()

            # 7. Безопасно сравниваем хеши
            if not hmac.compare_digest(calculated_hash, original_hash):
                raise AuthError("Неверная подпись данных MAX")

            # 8. Достаем user_id из JSON
            user_data = json.loads(user_str)
            return int(user_data['id'])

        except AuthError:
            raise
        except (ValueError, KeyError, json.JSONDecodeError):
            raise AuthError("Некорректный формат данных MAX")
        except Exception as e:
            raise AuthError(f"Ошибка авторизации MAX: {e}")


class VKAuthRepository(IVKAuthRepository):
    def __init__(self, client_secret: str):
        self._client_secret = client_secret

    async def verify_data(self, auth_data: str) -> int:
        try:
            # В VK WebApp / Bridge данные обычно приходят в виде query-строки или JSON.
            # Предполагаем, что auth_data — это query-строка параметров (key=value&...)
            params = dict(parse_qsl(auth_data, keep_blank_values=True))

            # Извлекаем подпись, которую передал клиент
            sign_param = params.pop('sign', None)
            user_id = params.get('user_id')

            if not sign_param or not user_id:
                raise AuthError("Отсутствуют обязательные параметры (sign/user_id)")

            # 1. Сортируем параметры по ключам (ksort в PHP)
            sorted_params = sorted(params.items())

            # 2. Формируем строку запроса (http_build_query в PHP)
            # ВАЖНО: В VK параметры должны кодироваться стандартным urlencode
            sign_params_query = urlencode(sorted_params)

            # 3. Вычисляем HMAC-SHA256 в бинарном виде (raw_output=true)
            raw_hash = hmac.new(
                key=self._client_secret.encode('utf-8'),
                msg=sign_params_query.encode('utf-8'),
                digestmod=hashlib.sha256
            ).digest()

            # 4. Кодируем в base64url (стандартный base64 с заменой +/ на -_ и удалением =)
            calculated_sign = (
                base64.b64encode(raw_hash)
                .decode('utf-8')
                .replace('+', '-')
                .replace('/', '_')
                .rstrip('=')
            )

            # 5. Проверяем подпись
            if not hmac.compare_digest(calculated_sign, sign_param):
                raise AuthError("Неверная подпись данных VK")

            return int(user_id)

        except AuthError:
            raise
        except (ValueError, KeyError):
            raise AuthError("Некорректный формат данных VK")
        except Exception as e:
            raise AuthError(f"Ошибка авторизации VK: {e}")