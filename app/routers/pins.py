import filetype
from typing import Annotated
from urllib.parse import urlparse
from uuid import UUID
from fastapi import APIRouter, File, UploadFile, HTTPException

from app.utils import get_path_segment
from app.services.aws import get_aws_service
from app.services.pins import PinsService
from app.models.common import ApiResponse
from app.models.pin import PinFormCreate, PinPublic
from app.deps import CurrentUser, SessionDep
from app.config import Settings


router = APIRouter()

settings = Settings()

@router.post("/pins")
async def store(pinFormCreate: PinFormCreate, user: CurrentUser, session: SessionDep, response_model=ApiResponse):
    if (not pinFormCreate.content or pinFormCreate.content.strip() == "") and (not pinFormCreate.url or pinFormCreate.url.strip() == "") and (not pinFormCreate.image_path or pinFormCreate.image_path.strip() == ""):
        raise HTTPException(status_code=422)

    if pinFormCreate.url:
        url_obj = urlparse(pinFormCreate.url)
        if not url_obj.netloc:
            raise HTTPException(status_code=422)

    if pinFormCreate.image_path:
        image_path_user_id = get_path_segment(pinFormCreate.image_path, 1)
        if image_path_user_id != str(user.id):
            raise HTTPException(status_code=400)
        aws_service = get_aws_service()
        image_path_meta = aws_service.get_s3_head_object(settings.ASSET_STORAGE_BUCKET_NAME, pinFormCreate.image_path)
        if not image_path_meta:
           raise HTTPException(status_code=400)

    pins_service = PinsService(session)
    pin = pins_service.store(pinFormCreate, user)
    session.refresh(pin)
    pin_public = PinPublic.model_validate(pin)
    return ApiResponse(data=pin_public)

@router.post("/pins/file")
async def file_store(
    up_file: Annotated[UploadFile, File()],
    user: CurrentUser
):
    file_content = await up_file.read()
    file_size = len(file_content)
    if file_size > 5242880:
        raise HTTPException(status_code=400, detail="File size is too large")

    file_type = filetype.guess(file_content)
    if file_type is None or file_type.mime not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="File type is not supported")

    upLoadResult = PinsService.uplpad_file(file_content, user)
    if upLoadResult is False:
        raise HTTPException(status_code=500)
    return ApiResponse(data=upLoadResult)

@router.put("/pins/{id}")
async def update(id: str, user: CurrentUser):
    return ""

@router.delete("/pins/{id}")
def destroy(id: UUID, user: CurrentUser, session: SessionDep, response_model=ApiResponse):
    pins_service = PinsService(session)

    pin = pins_service.get_by_id_and_user(id, user.id)
    if not pin:
        raise HTTPException(status_code=404)

    pins_service.delete_by_id(id)
    return ApiResponse()
