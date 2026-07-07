from fastapi import Depends, Header, HTTPException, status
from src.core.containers import Container
from src.services.interfaces import (IAuthService, IUserService, IPetitionService, 
                                     ICandidateService, IAdminPetitionService, IStatsService)
from src.domain.entities.user import User, UserRole
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

async def get_candidate_service(container: Container = Depends(get_container)) -> ICandidateService:
    return container.candidate_service()

async def get_admin_petition_service(container: Container = Depends(get_container)) -> IAdminPetitionService:
    return container.admin_petition_service()

async def get_stats_service(container: Container = Depends(get_container)) -> IStatsService:
    return container.stats_service()

async def get_admin_candidate_service(container: Container = Depends(get_container)) -> IAdminCandidateService:
    return container.admin_candidate_service()

async def get_cabinet_petition_service(container: Container = Depends(get_container)) -> ICabinetPetitionService:
    return container.cabinet_petition_service()

async def get_cabinet_question_service(container: Container = Depends(get_container)) -> ICabinetQuestionService:
    return container.cabinet_question_service()

async def get_upload_service(container: Container = Depends(get_container)) -> IUploadService:
    return container.upload_service()

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

def require_role(allowed_roles: list[UserRole]):
    async def role_checker(user: User = Depends(get_current_user)):
        if user.role not in allowed_roles:
            raise HTTPException(status_code=403, detail={"error": "FORBIDDEN_ROLE", "message": "Недостаточно прав"})
        return user
    return role_checker
