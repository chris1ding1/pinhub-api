from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field

from app.deps import CurrentUser
from app.services.auth import get_auth_service
from app.models.common import ApiResponse
from app.models.user import UserAuth


router = APIRouter()

class AuthEmail(BaseModel):
    email: EmailStr = Field(max_length=255)

class AuthEmailVerify(AuthEmail):
    verifyCode: str = Field(min_length=6, max_length=6)

@router.post("/auth/email/send")
async def auth_email_send(authEmail: AuthEmail, response_model=ApiResponse):
    send_resault = await get_auth_service().send_auth_verify_email(authEmail.email, "Please verify your email address")

    if send_resault:
        return ApiResponse()

    raise HTTPException(status_code=400)

@router.post("/auth/email/verify")
async def auth_email_verify(authEmailVerify: AuthEmailVerify, response_model=ApiResponse):
    verify_resault = await get_auth_service().verify_email(authEmailVerify.email, authEmailVerify.verifyCode)

    if isinstance(verify_resault, UserAuth):
        return ApiResponse(data=verify_resault)

    raise HTTPException(status_code=400)

@router.post("/logout")
async def logout(user: CurrentUser, response_model=ApiResponse):
    """Logout. TODO: Clear token"""
    return ApiResponse()
