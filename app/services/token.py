import time
import uuid

import boto3
import jwt
from botocore.exceptions import ClientError
from pydantic import BaseModel

from app.config import Settings

settings = Settings()


class Token(BaseModel):
    jwt_id: str
    user_id: str
    token_type: str
    issued_at: int
    expiration_time: int
    is_revoked: bool = False
    revoked_at: int | None = None
    created_at: int


def encoded_token(subject: str) -> str:
    expiration_time = int(time.time()) + settings.ACCESS_TOKEN_EXPIRE_SECOND
    payload = {
        "exp": expiration_time,
        "sub": str(subject),
        "jti": str(uuid.uuid4()),
        "iat": int(time.time()),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decoded_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


class TokenService:
    def __init__(self):
        if settings.ENVIRONMENT == "local":
            self.dynamodb = boto3.resource(
                "dynamodb",
                region_name=settings.AWS_DEFAULT_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            )
        else:
            self.dynamodb = boto3.resource(
                "dynamodb",
                region_name=settings.AWS_DEFAULT_REGION,
            )
        self.dynamodbTable = self.dynamodb.Table(settings.TOKENS_TABLE_NAME)

    def store(self, user_id: str) -> str:
        token_encoded = encoded_token(user_id)
        token_payload = decoded_token(token_encoded)

        token_record = Token(
            jwt_id=token_payload["jti"],
            user_id=user_id,
            token_type="access",
            issued_at=token_payload["iat"],
            expiration_time=token_payload["exp"],
            created_at=int(time.time()),
        )

        try:
            self.dynamodbTable.put_item(Item=token_record.model_dump())
        except ClientError as err:
            raise err

        return token_encoded


def get_token_service():
    return TokenService()
