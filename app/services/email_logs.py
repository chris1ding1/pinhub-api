import logging
import time
import uuid
from enum import IntEnum
from typing import Any

import boto3
from botocore.exceptions import ClientError
from pydantic import BaseModel, EmailStr

from app.config import Settings

settings = Settings()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailLogStatus(IntEnum):
    PENDING = 1
    SUCCESS = 2
    FAILED = 3

class EmailLogTypes(IntEnum):
    VERIFY_ADDRESS = 1

class EmailLogBase(BaseModel):
    id: str
    email_address: EmailStr
    business_type: EmailLogTypes
    send_status: EmailLogStatus
    expires_timestamp: int | None = None
    provider: str
    provider_id: str | None = None
    provider_response: Any
    create_timestamp: int

class EmailLogVerify(EmailLogBase):
    verify_code: str

class EmailLogService:
    def __init__(self):
        if settings.ENVIRONMENT == "local":
            self.dynamodb = boto3.resource(
                'dynamodb',
                region_name=settings.AWS_DEFAULT_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            )
        else:
            self.dynamodb = boto3.resource(
                'dynamodb',
                region_name=settings.AWS_DEFAULT_REGION,
            )
        self.dynamodbTable = self.dynamodb.Table(settings.EMAIL_LOGS_TABLE_NAME)

    async def store(
        self,
        email_address: EmailStr,
        business_type: EmailLogTypes,
        send_status: EmailLogStatus,
        verify_code: str,
        expires_timestamp: int | None,
        provider: str,
        provider_id: str | None,
        provider_response: Any,
    ):

        email_log = EmailLogVerify(
            id=str(uuid.uuid4()),
            email_address=email_address,
            business_type=business_type,
            send_status=send_status,
            verify_code=str(verify_code),
            expires_timestamp=expires_timestamp,
            provider=provider,
            provider_id=provider_id,
            provider_response=provider_response,
            create_timestamp = int(time.time())
        )

        try:
            self.dynamodbTable.put_item(
                Item=email_log.model_dump()
            )
        except ClientError as err:
            raise err

    async def query_by_filter(self, filter_expr: str):
        response = self.dynamodbTable.scan(FilterExpression=filter_expr)
        return response.get("Items", [])
