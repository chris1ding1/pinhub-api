from enum import Enum, IntEnum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PinType(str, Enum):
    URL = "url"
    TEXT = "text"
    AUDIO = "audio"
    IMAGE = "image"

class Visibility(IntEnum):
    PRIVATE = 1
    PUBLIC = 2

class Pin(BaseModel):
    type: PinType
    uid: str
    title: Optional[str] = None
    content: Optional[str] = None
    url: Optional[str] = None
    audio_path: Optional[str] = None
    image_path: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    visibility: Visibility = Visibility.PRIVATE
    owner_id: str
    deleted_at: Optional[int] = None
    created_at: int
    updated_at: int
