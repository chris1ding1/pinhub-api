import secrets
from typing import Annotated, Any, Literal
from urllib.parse import urlparse

from pydantic import AnyUrl, BeforeValidator, EmailStr, PostgresDsn, computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    APP_NAME: str
    APP_URL: str = "http://localhost:3000"
    APP_TIMEZONE: str = "UTC"
    APP_LOCALE: str

    FRONTEND_ASSET_URL: str
    DEFAULT_AVATAR_PATH: str = "/images/avatars/default.png"

    MAIL_MAILER: Literal["postmark", "ses"] | None = None
    MAIL_FROM_ADDRESS: EmailStr | None = None

    ENVIRONMENT: Literal["local", "staging", "production"] = "local"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    # 604800s = 7 days
    ACCESS_TOKEN_EXPIRE_SECOND: int = 604800
    BACKEND_CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = (
        []
    )

    @computed_field
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [
            self.APP_URL
        ]

    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    AWS_DEFAULT_REGION: str | None = None

    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_SECRET: str | None = None

    GITHUB_CLIENT_ID: str | None = None
    GITHUB_CLIENT_SECRET: str | None = None

    POSTMARK_ENDPOINT_URL: str = "https://api.postmarkapp.com"

    @computed_field
    @property
    def POSTMARK_EMAIL_SINGLE(self) -> str:
        return f"{self.POSTMARK_ENDPOINT_URL}/email"

    @computed_field
    @property
    def POSTMARK_EMAIL_BATCH(self) -> str:
        return f"{self.POSTMARK_ENDPOINT_URL}/email/batch"

    POSTMARK_TOKEN: str | None = None

    PAGE_SIZE: int = 20

    POSTGRES_HOST: str | None = None
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str | None = None
    POSTGRES_DB: str | None = None

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    @computed_field
    @property
    def EMAIL_LOGS_TABLE_NAME(self) -> str:
        return f"{self.ENVIRONMENT}_{self.APP_NAME}_email_logs".lower()

    @computed_field
    @property
    def TOKENS_TABLE_NAME(self) -> str:
        return f"{self.ENVIRONMENT}_{self.APP_NAME}_tokens".lower()

    @computed_field
    @property
    def ASSET_STORAGE_BUCKET_NAME(self) -> str:
        parsed_url = urlparse(self.FRONTEND_ASSET_URL)
        domain = parsed_url.netloc

        return f"{self.ENVIRONMENT}.{domain}".lower()
