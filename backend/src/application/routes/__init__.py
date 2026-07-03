from fastapi import APIRouter
from .auth import router as auth_router
from .me import router as me_router
from .petitions import router as petitions_router

root_router = APIRouter()
root_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
root_router.include_router(me_router, prefix="", tags=["Profile"])
root_router.include_router(petitions_router, prefix="/petitions", tags=["Petitions"])
