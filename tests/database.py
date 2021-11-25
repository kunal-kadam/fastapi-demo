from fastapi.testclient import TestClient
from pydantic.networks import import_email_validator
from sqlalchemy.sql.expression import bindparam
from main import app
from app.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.orm_db import get_db
from app.orm_db import Base
import pytest
from alembic import command

SQLALCHEMY_DATABASE_URL  = f'postgresql://postgres:password123@localhost:5432/fastapi_test'

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()



def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()




# client = TestClient(app)

@pytest.fixture(scope="function")
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

    