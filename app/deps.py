from collections.abc import Generator
from typing import Annotated
import uuid

from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session

from app.db import engine
from app.models.user import User
from app.services.token import decoded_token
from app.services.users import get_user_service

def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

security = HTTPBearer()

SessionDep = Annotated[Session, Depends(get_db)]
credentialsDep = Annotated[HTTPAuthorizationCredentials, Depends(security)]

def get_current_user(credentials: credentialsDep) -> User:

    auth_failed_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decoded_token(credentials.credentials)
    except (InvalidTokenError, ValidationError):
        raise auth_failed_exception

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise auth_failed_exception

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise auth_failed_exception

    user = get_user_service().get_user_by_id(user_id)
    if not user:
        raise auth_failed_exception
    return user

CurrentUser = Annotated[User, Depends(get_current_user)]
