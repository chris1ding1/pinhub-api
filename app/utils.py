import secrets
import string
import time

from httpx import AsyncClient as HttpxAsyncClient
from pydantic import BaseModel, EmailStr

from app.config import Settings
from app.services.email_logs import EmailLogService, EmailLogStatus, EmailLogTypes

settings = Settings()

def generate_random_string(length=6):
    charset = string.digits + string.ascii_lowercase
    return ''.join(secrets.choice(charset) for _ in range(length))

class SendEmail(BaseModel):
    From: str = settings.MAIL_FROM_ADDRESS
    To: str
    Subject: str | None = None

class PostmarkEmailBody(SendEmail):
    TextBody: str | None = None
    HtmlBody: str | None = None
    MessageStream: str = "outbound"

class PostmarkEmailResponse(BaseModel):
    To: str | None = None
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

def verify_email_html_content(verification_code: str):
    return f"""
    <html>
        <body>
            <p>Please use this code to verify your {settings.APP_NAME} email address:</p>
            <h2>{verification_code}</h2>
        </body>
    </html>
    """

async def send_email(to_mail: EmailStr, subject: str = "", mailer = settings.MAIL_MAILER):
    verification_code = generate_random_string()
    html_content = verify_email_html_content(verification_code)
    data = PostmarkEmailBody(
        To=to_mail,
        Subject=subject,
        HtmlBody=html_content
    )
    send_resault = await postmark_email(data)

    if send_resault.ErrorCode == 0:
        status = EmailLogStatus.SUCCESS
        expires_timestamp = int(time.time()) + (5 * 60)
    else:
        expires_timestamp = None
        status = EmailLogStatus.FAILED

    await EmailLogService().store(to_mail, EmailLogTypes.VERIFY_ADDRESS, status, expires_timestamp, mailer, send_resault.MessageID, send_resault.model_dump())

    return send_resault

