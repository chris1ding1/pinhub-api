from fastapi import APIRouter
from pydantic import BaseModel, EmailStr, Field
from app.services.auth import get_auth_service

router = APIRouter()

class AuthEmail(BaseModel):
    email: EmailStr = Field(max_length=255)

class AuthEmailVerify(AuthEmail):
    verifyCode: str = Field(min_length=6, max_length=6)

@router.post("/auth/email/send")
async def auth_email_send(authEmail: AuthEmail):
    return await get_auth_service().send_auth_verify_email(authEmail.email, "Please verify your email address")

@router.post("/auth/email/verify")
async def auth_email_verify(authEmailVerify: AuthEmailVerify):
    return {"email": authEmailVerify.email, "verifyCode": authEmailVerify.verifyCode}
