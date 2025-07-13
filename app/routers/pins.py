import filetype
from typing import Annotated
from urllib.parse import urlparse
from uuid import UUID
from fastapi import APIRouter, File, UploadFile, HTTPException

from app.utils import get_path_segment
from app.services.aws import get_aws_service
from app.services.pins import PinsService
from app.models.common import ApiResponse, IndexBase
from app.models.pin import PinFormCreate, PinPublic, PinsPublicResponse
from app.deps import CurrentUser, SessionDep
from app.config import Settings


router = APIRouter()

settings = Settings()

@router.get("/pins")
async def index(session: SessionDep, response_model=ApiResponse):
    pins_service = PinsService(session)
    pins = pins_service.index_by_public()

    return ApiResponse(
        data=IndexBase(
            items=PinsPublicResponse(data=pins).data,
        )
    )

@router.post("/pins")
async def store(pinFormCreate: PinFormCreate, user: CurrentUser, session: SessionDep, response_model=ApiResponse):
    if (not pinFormCreate.content or pinFormCreate.content.strip() == "") and (not pinFormCreate.url or pinFormCreate.url.strip() == "") and (not pinFormCreate.image_path or pinFormCreate.image_path.strip() == "") and (not pinFormCreate.audio_path or pinFormCreate.audio_path.strip() == ""):
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

    if pinFormCreate.audio_path:
        audio_path_user_id = get_path_segment(pinFormCreate.audio_path, 1)
        if audio_path_user_id != str(user.id):
            raise HTTPException(status_code=400)
        aws_service = get_aws_service()
        audio_path_meta = aws_service.get_s3_head_object(settings.ASSET_STORAGE_BUCKET_NAME, pinFormCreate.audio_path)
        if not audio_path_meta:
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

@router.post("/pins/image")
async def store_image_pin(
    file: Annotated[UploadFile, File()],
    user: CurrentUser,
    session: SessionDep,
    response_model=ApiResponse
):
    file_content = await file.read()
    file_size = len(file_content)
    if file_size > 5242880:
        raise HTTPException(status_code=400, detail="File size is too large")

    file_type = filetype.guess(file_content)
    if file_type is None or file_type.mime not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="File type is not supported")

    pins_service = PinsService(session)
    pin = pins_service.store_image_pin(file_content, user)
    pin_public = PinPublic.model_validate(pin)
    return ApiResponse(data=pin_public)

@router.put("/pins/{id}")
async def update(id: str, user: CurrentUser):
    return ""

@router.delete("/pins/{id}")
async def destroy(id: UUID, user: CurrentUser, session: SessionDep, response_model=ApiResponse):
    pins_service = PinsService(session)

    pin = pins_service.get_by_id_and_user(id, user.id)
    if not pin:
        raise HTTPException(status_code=404)

    pins_service.delete_by_id(id)
    return ApiResponse()

@router.post("/pins/audio")
async def audio_store(
    audio_file: Annotated[UploadFile, File()],
    user: CurrentUser
):
    file_content = await audio_file.read()

    file_type = filetype.guess(file_content)
    print(f"file_content: {file_type.mime}")
    if file_type is None or file_type.mime != "video/webm":
        raise HTTPException(status_code=400, detail="File type is not supported")

    upLoadResult = PinsService.uplpad_file(file_content, user)
    if upLoadResult is False:
        raise HTTPException(status_code=500)
    return ApiResponse(data=upLoadResult)
