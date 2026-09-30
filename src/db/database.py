# Stores information about database structures such as
# table names, schemas, columns, and column types
from sqlalchemy import MetaData, create_engine

# Session is used to communicate with the database
# sessionmaker creates a new database session for each request
from sqlalchemy.orm import (
    DeclarativeBase,
    Session,
    sessionmaker,
)

from src.core.config import DATABASE_URL, DEFAULT_SCHEMA_NAME

metadata = MetaData(
    schema=DEFAULT_SCHEMA_NAME
)

# Parent class for all SQLAlchemy database models
class Base(DeclarativeBase):
    metadata = metadata

# Creates the synchronous SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    echo=True,
)

# Creates a new synchronous session
SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    autoflush=False,
    expire_on_commit=False,
)

# FastAPI database dependency
def get_db():
    session = SessionLocal()

    try:
        yield session

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()