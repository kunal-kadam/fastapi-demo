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
from app.oauth2 import create_access_token
import pytest
from alembic import command
from app import models
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


@pytest.fixture
def test_user2(client):
    user_data = {"email":"komal@gmail.com", "password": "password"}
    res = client.post("/users/", json=user_data)
    new_user = res.json()
    new_user["password"] = user_data["password"]
    assert res.status_code == 201
    return new_user

@pytest.fixture
def test_user(client):
    user_data = {"email":"swati@gmail.com", "password": "kadam"}
    res = client.post("/users/", json=user_data)
    new_user = res.json()
    new_user["password"] = user_data["password"]
    assert res.status_code == 201
    return new_user

@pytest.fixture
def token(test_user):
    return create_access_token({"user_id":test_user['id']})

@pytest.fixture
def authorized_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    return client

def create_post_model(post):
    return models.Post(**post)

@pytest.fixture
def test_posts(test_user, session, test_user2):
    post_data = [{
        "title": "first title",
        "content" : "first content",
        "user_id" : test_user['id']
    }, {
        "title": "second title",
        "content" : "second content",
        "user_id" : test_user['id']
    }, {
        "title": "third title",
        "content" : "third content",
        "user_id" : test_user['id']
    }, {
        "title": "fourth title",
        "content" : "fourth content",
        "user_id" : test_user2['id']
    }]

    post_map = map(create_post_model, post_data)
    posts = list(post_map)
    session.add_all(posts)
    session.commit()
    posts = session.query(models.Post).all()
    return posts