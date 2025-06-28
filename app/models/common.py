from typing import Any, List
from enum import IntEnum
from pydantic import BaseModel
from app.config import Settings

settings = Settings()

class StatusCode(IntEnum):
    SUCCESS = 0
    AUTH_EMAIL_USER_NOT_EXIST = 101001

class ApiResponse(BaseModel):
    code: StatusCode = StatusCode.SUCCESS
    data: Any | None = None

class IndexResourceData(BaseModel):
    total: int = 0
    page: int = 1
    page_size: int = settings.PAGE_SIZE
    next_page: int = 0
    prev_page: int = 0
    items: List[Any] = []

class IndexResource(ApiResponse):
    data: IndexResourceData = None
