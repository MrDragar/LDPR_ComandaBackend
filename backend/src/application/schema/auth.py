from datetime import date
from typing import Optional

from pydantic import BaseModel


class TelegramAuthData(BaseModel):
    initData: str


class JWTToken(BaseModel):
    token: str
    
    
class MeResponse(BaseModel):
    id: int
    is_member: bool
    username: str | None
    surname: str
    name: str
    patronymic: str | None
    birth_date: date
    phone_number: str
    region: str
    email: str
    gender: str
    city: str
    wish_to_join: bool
    home_address: str | None
    news_subscription: bool
