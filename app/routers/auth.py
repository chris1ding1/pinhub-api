from fastapi import APIRouter
from pydantic import BaseModel, EmailStr, Field

from app.utils import send_email

router = APIRouter()

class AuthEmail(BaseModel):
    email: EmailStr = Field(max_length=255)

class AuthEmailVerify(AuthEmail):
    verifyCode: str = Field(min_length=6, max_length=6)

@router.post("/auth/email/send")
async def auth_email_send(authEmail: AuthEmail):
    return await send_email(authEmail.email, "Please verify your email address")

@router.post("/auth/email/verify")
async def auth_email_verify(authEmailVerify: AuthEmailVerify):
    return {"email": authEmailVerify.email, "verifyCode": authEmailVerify.verifyCode}
