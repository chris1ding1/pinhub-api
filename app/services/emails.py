from httpx import AsyncClient as HttpxAsyncClient
from pydantic import BaseModel, EmailStr

import boto3
from botocore.exceptions import ClientError as BotoClientError

from app.config import Settings

settings = Settings()

class SendEmail(BaseModel):
    From: EmailStr = settings.MAIL_FROM_ADDRESS
    To: EmailStr
    Subject: str | None = None

class PostmarkEmailBody(SendEmail):
    TextBody: str | None = None
    HtmlBody: str | None = None
    MessageStream: str = "outbound"

class PostmarkEmailResponse(BaseModel):
    To: EmailStr | None = None
    SubmittedAt: str | None = None
    MessageID: str | None = None
    ErrorCode: int
    Message: str

async def postmark_email(body: PostmarkEmailBody | list[PostmarkEmailBody]) -> PostmarkEmailResponse | list[PostmarkEmailResponse]:
    if isinstance(body, list):
        url = settings.POSTMARK_EMAIL_BATCH
        payload = [item.model_dump() for item in body]
    else:
        url = settings.POSTMARK_EMAIL_SINGLE
        payload = body.model_dump()

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Postmark-Server-Token": settings.POSTMARK_TOKEN
    }

    async with HttpxAsyncClient() as client:
        response= await client.post(
            url,
            json=payload,
            headers=headers
        )
        response_data = response.json()

        if isinstance(body, list):
            return [PostmarkEmailResponse(**item) for item in response_data]
        else:
            return PostmarkEmailResponse(**response_data)

class SESEmailBody(SendEmail):
    TextBody: str | None = None
    HtmlBody: str | None = None

class SESEmailResponse(BaseModel):
    MessageID: str | None = None
    ErrorCode: int = 0
    ResponseMetadata: dict

async def ses_email(email: SESEmailBody) -> SESEmailResponse:
    if settings.ENVIRONMENT == "local":
        ses_client = boto3.client(
            'ses',
            region_name=settings.AWS_DEFAULT_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
    else:
        ses_client = boto3.client(
            'ses',
            region_name=settings.AWS_DEFAULT_REGION,
        )
    email_message = {
        'Subject': {'Data': email.Subject},
        'Body': {}
    }
    if email.TextBody:
        email_message['Body']['Text'] = {'Data': email.TextBody}
    if email.HtmlBody:
        email_message['Body']['Html'] = {'Data': email.HtmlBody}

    try:
        response = ses_client.send_email(
            Source=email.From,
            Destination={'ToAddresses': [email.To]},
            Message=email_message
        )

        return SESEmailResponse(**response)
    except BotoClientError as err:
        return SESEmailResponse(
            ErrorCode=getattr(err, 'response', {}).get('Error', {}).get('Code', 999),
            ResponseMetadata={'Error': str(err)}
        )
