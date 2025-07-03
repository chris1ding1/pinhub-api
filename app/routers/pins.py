import filetype
from typing import Annotated

from fastapi import APIRouter, File, UploadFile, HTTPException

from app.services.pins import PinsService
from app.models.common import ApiResponse
from app.models.pin import PinFormCreate, PinPublic
from app.deps import CurrentUser, SessionDep
from app.config import Settings


router = APIRouter()

settings = Settings()

@router.post("/pins")
async def store(pinFormCreate: PinFormCreate, user: CurrentUser, session: SessionDep, response_model=ApiResponse):
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
def destroy(id: str, user: CurrentUser):
    return ""
