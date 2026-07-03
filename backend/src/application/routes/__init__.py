from fastapi import APIRouter
from .auth import router as auth_router
from .me import router as me_router
from .petitions import router as petitions_router
from .admin import router as admin_router
from .candidates import router as candidates_router
from .referral import router as referral_router
from .stats import router as stats_router

root_router = APIRouter()
root_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
root_router.include_router(me_router, prefix="", tags=["Profile"])
root_router.include_router(petitions_router, prefix="/petitions", tags=["Petitions"])
root_router.include_router(candidates.router, prefix="/candidates", tags=["Candidates"])
root_router.include_router(admin_router, prefix="/admin", tags=["Admin"])
root_router.include_router(stats_router, prefix="/stats", tags=["Stats"])
root_router.include_router(referral_router, prefix="/referral", tags=["Referral"])