from httpx import AsyncClient as HttpxAsyncClient
from pydantic import BaseModel, EmailStr

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
