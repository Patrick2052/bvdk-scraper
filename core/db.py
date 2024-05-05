from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from core.config import settings


# Create the engine
engine = create_engine(
    settings.postgres_dsn
)

DatabaseSession = sessionmaker(bind=engine)

Base = declarative_base()
