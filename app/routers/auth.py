from fastapi import APIRouter
from pydantic import BaseModel, EmailStr, Field

from app.utils import send_email

router = APIRouter()

class AuthEmail(BaseModel):
    email: EmailStr = Field(max_length=255)

@router.post("/auth/email/send")
async def auth_redirect(authEmail: AuthEmail):
    return await send_email(authEmail.email, "Please verify your email address")

@router.post("/auth/email/verify")
async def auth_callback():
    return "xxx"
