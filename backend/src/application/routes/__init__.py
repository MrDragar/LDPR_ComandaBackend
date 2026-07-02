from fastapi import APIRouter
from .auth import router as auth_router

root_router = APIRouter()
root_router.include_router(auth_router)
