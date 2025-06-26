import time
import secrets
from typing import Optional
from pydantic import EmailStr
from sqlmodel import Session, select
from app.db import engine
from app.models.user import User
from app.config import Settings

settings = Settings()

class UserService:
    def get_user_by_email(self, email: EmailStr) -> Optional[User]:
        with Session(engine) as session:
            statement = select(User).where(
                User.email == email,
                # User.deleted_at.is_(None)
            )
            return session.exec(statement).first()

    def create_user_by_email(self, email: EmailStr) -> User:
        """Create a new user"""
        current_time = int(time.time())

        email_username = email.split('@')[0]
        username = self.make_username(email_username)

        user = User(
            username=username,
            name=username,
            email=email,
            email_verified_at=current_time,
            created_at=current_time,
            updated_at=current_time
        )

        with Session(engine) as session:
            session.add(user)
            session.commit()
            session.refresh(user)
            return user

    def make_username(self, username: str) -> str:
        if not self.username_exists(username):
            return username

        while True:
            random_number = secrets.randbelow(10000)
            new_username = f"{username}{random_number}"

            if not self.username_exists(new_username):
                return new_username

    def username_exists(self, username: str) -> bool:
        with Session(engine) as session:
            statement = select(User).where(
                User.username == username
            )
            return session.exec(statement).first() is not None

def get_user_service():
    return UserService()
