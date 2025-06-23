from fastapi import APIRouter
from pydantic import BaseModel, EmailStr, Field

router = APIRouter()

class AuthEmail(BaseModel):
    email: EmailStr = Field(max_length=255)

@router.post("/auth/email/send")
async def auth_redirect(authEmail: AuthEmail):
    return authEmail

@router.post("/auth/email/verify")
async def auth_callback():
    return "xxx"
