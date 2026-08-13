import os

from app.db import models
import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv(".env.test")

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

TestingSessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


@pytest.fixture(scope="session")
def db_engine():
    return engine


@pytest.fixture(scope="function")
def db(db_engine):
    connection = db_engine.connect()

    transaction = connection.begin()

    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()

    transaction.rollback()

    connection.close()