from typing import Any
from enum import IntEnum
from pydantic import BaseModel

class StatusCode(IntEnum):
    SUCCESS = 0

class ApiResponse(BaseModel):
    code: StatusCode = StatusCode.SUCCESS
    data: Any | None = None
