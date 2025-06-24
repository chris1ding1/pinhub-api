from fastapi import APIRouter
from pydantic import BaseModel, EmailStr, Field
from app.utils import send_email, generate_random_string
from app.config import Settings

settings = Settings()

router = APIRouter()

class AuthEmail(BaseModel):
    email: EmailStr = Field(max_length=255)

@router.post("/auth/email/send")
async def auth_redirect(authEmail: AuthEmail):

    verification_code = generate_random_string()
    email_html_content = f"""
    <html>
        <body>
            <p>Please use this code to verify your {settings.APP_NAME} email address:</p>
            <h2>{verification_code}</h2>
        </body>
    </html>
    """
    return await send_email(authEmail.email, f"Please verify your email address for {settings.APP_NAME}", email_html_content)

@router.post("/auth/email/verify")
async def auth_callback():
    return "xxx"
