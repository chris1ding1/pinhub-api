from typing import Any, List
from enum import IntEnum
from pydantic import BaseModel
from app.config import Settings

settings = Settings()

class StatusCode(IntEnum):
    SUCCESS = 0

class ApiResponse(BaseModel):
    code: StatusCode = StatusCode.SUCCESS
    data: Any | None = None

class IndexResource(BaseModel):
    total: int = 0
    page: int = 1
    page_size: int = settings.PAGE_SIZE
    next_page: int = 0
    prev_page: int = 0
    items: List[Any]
