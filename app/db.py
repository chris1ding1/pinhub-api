"""DB Core"""

from sqlmodel import SQLModel, create_engine

from app.config import Settings

settings = Settings()
engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI), echo=True)


def create_db_and_tables():
    """Create DB and Tables"""
    SQLModel.metadata.create_all(engine)
