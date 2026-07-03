import logging
from src.domain.entities.petition import PetitionStatus
from src.domain.exceptions import PetitionError, PetitionAlreadyModeratedError
from src.domain.interfaces import IPetitionRepository, IUnitOfWork
from src.services.interfaces import IAdminPetitionService

logger = logging.getLogger(__name__)


class AdminPetitionService(IAdminPetitionService):
    def __init__(self, petition_repo: IPetitionRepository, uow: IUnitOfWork):
        self.__petition_repo = petition_repo
        self.__uow = uow

    async def approve_petition(self, petition_id: int) -> dict:
        async with self.__uow.atomic():
            petition = await self.__petition_repo.get_by_id(petition_id)
            if not petition:
                raise PetitionError("Петиция не найдена")
            if petition.status != PetitionStatus.MODERATION:
                raise PetitionAlreadyModeratedError("Петиция уже была модерирована")

            await self.__petition_repo.update_status(petition_id, PetitionStatus.PUBLISHED)
            return {"status": "published", "message": "Петиция одобрена и опубликована"}

    async def reject_petition(self, petition_id: int, reason: str) -> dict:
        async with self.__uow.atomic():
            petition = await self.__petition_repo.get_by_id(petition_id)
            if not petition:
                raise PetitionError("Петиция не найдена")
            if petition.status != PetitionStatus.MODERATION:
                raise PetitionAlreadyModeratedError("Петиция уже была модерирована")

            await self.__petition_repo.update_status(petition_id, PetitionStatus.REJECTED)
            return {"status": "rejected", "message": "Петиция отклонена"}
