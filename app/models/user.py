import uuid

from pydantic import EmailStr
from sqlmodel import Field, SQLModel

from app.config import Settings

settings = Settings()

class UserBase(SQLModel):
    username: str = Field(max_length=64)
    name: str = Field(max_length=255)
    avatar_path: str | None = Field(default=None, max_length=255)
    bio: str | None = Field(default=None, max_length=512)
    locale: str = Field(default=settings.APP_LOCALE)
    timezone: str = Field(default=settings.APP_TIMEZONE)


class User(UserBase, table=True):
    __tablename__ = "users"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    email_verified_at: int | None = Field(default=None)
    deleted_at: int | None = Field(default=None)
    created_at: int
    updated_at: int
