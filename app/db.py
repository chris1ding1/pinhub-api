from sqlmodel import SQLModel, create_engine
from app.config import Settings

engine = create_engine(str(Settings.SQLALCHEMY_DATABASE_URI), echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)