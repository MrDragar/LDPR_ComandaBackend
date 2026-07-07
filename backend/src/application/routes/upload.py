from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from src.application.dependencies import get_current_user, get_upload_service
from src.domain.entities.user import User
from src.services.interfaces import IUploadService

router = APIRouter()


class PresignedUrlResponse(BaseModel):
    upload_url: str
    file_url: str


@router.get("/presigned-url", response_model=PresignedUrlResponse)
async def get_presigned_url(
        filename: str = Query(..., description="Original filename with extension"),
        content_type: str = Query(..., description="MIME type, e.g., image/jpeg"),
        user: User = Depends(get_current_user),
        upload_service: IUploadService = Depends(get_upload_service)):
    if not filename or not content_type:
        raise HTTPException(status_code=400, detail={"error": "INVALID_PAYLOAD",
                                                     "message": "filename and content_type are required"})

    return await upload_service.get_presigned_url(filename, content_type)
