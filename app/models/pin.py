import uuid
import time
from urllib.parse import urljoin, urlparse
from enum import IntEnum
from typing import Any, Dict, List, Annotated

from pydantic import ConfigDict, computed_field
from sqlmodel import Field, SQLModel, JSON
from sqlalchemy import Integer
from sqlalchemy.dialects.postgresql import JSONB

from app.config import Settings

settings = Settings()

class Visibility(IntEnum):
    PRIVATE = 1
    PUBLIC = 2

class PinBase(SQLModel):
    model_config = ConfigDict(use_enum_values=True, str_strip_whitespace=True)

    content: str | None = Field(default=None, max_length=3000)
    url: str | None = Field(default=None, max_length=2048)
    audio_path: str | None = Field(default=None, max_length=255)
    image_path: str | None = Field(default=None, max_length=255)
    tags: Annotated[List[str], Field(default_factory=list, sa_type=JSONB)]
    visibility: Visibility = Field(default=Visibility.PRIVATE, sa_type=Integer)

class PinFormCreate(PinBase):
    pass

class Pin(PinBase, table=True):
    __tablename__ = "pins"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False)
    image_path: str | None = Field(default=None, max_length=255)
    extra: Annotated[Dict[str, Any], Field(default_factory=dict, sa_type=JSON)]
    deleted_at: int | None = Field(default=None)
    created_at: int = Field(default_factory=lambda: int(time.time()))
    updated_at: int = Field(default_factory=lambda: int(time.time()))

class PinPublic(Pin):
    @computed_field
    def audio_url(self) -> str | None:
        if self.audio_path:
            return urljoin(settings.FRONTEND_ASSET_URL, self.audio_path)
        return None

    @computed_field
    def image_url(self) -> str | None:
        if self.image_path:
            return urljoin(settings.FRONTEND_ASSET_URL, self.image_path)
        return None

    @computed_field
    def url_host(self) -> str | None:
        if self.url:
            try:
                parsed = urlparse(self.url)
                return parsed.netloc
            except Exception:
                return None
        return None

class PinsPublic(SQLModel):
    data: list[PinPublic]
    count: int

class PinPublicResponse(Pin):
    id: uuid.UUID
    content: str | None = None
    url: str | None = None
    image_path: str | None = None
    audio_path: str | None = None

    @computed_field
    def audio_url(self) -> str | None:
        if self.audio_path:
            return urljoin(settings.FRONTEND_ASSET_URL, self.audio_path)
        return None

    @computed_field
    def image_url(self) -> str | None:
        if self.image_path:
            return urljoin(settings.FRONTEND_ASSET_URL, self.image_path)
        return None

    @computed_field
    def url_host(self) -> str | None:
        if self.url:
            try:
                parsed = urlparse(self.url)
                return parsed.netloc
            except Exception:
                return None
        return None

class PinsPublicResponse(SQLModel):
    data: list[PinPublicResponse]
