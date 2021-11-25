import pytest 
from app import schemas
from app.config import Settings
# from .database import client, session
from jose import jwt
from app.config import settings


def test_root(client):
    res = client.get("/")
    # print(res.json().get('message'))
    assert res.json().get('message') == 'Hello World!!'
    assert res.status_code == 200

def test_create_user(client):
    res = client.post("/users/", json={"email" : "komal@gmail.com", "password" : "kadam"})
    # print(res.json())
    new_user = schemas.UserOut(**res.json())
    assert new_user.email == "komal@gmail.com"
    assert res.status_code == 201

def test_login_user(client, test_user):
    res = client.post("/login", data = {"username":test_user['email'], "password":test_user['password']})
    login_res = schemas.Token(**res.json())
    payload = jwt.decode(login_res.access_token, settings.secret_key, settings.algorithm)
    id = payload.get("user_id")
    assert id == test_user['id']
    assert login_res.token_type == "bearer"
    assert res.status_code == 200

@pytest.mark.parametrize("email, password, status_code", [
    ('swati@gmail.com', 'wrong', 403),
    ('wrong@gmail.com', 'kadam', 403),
    ('wrong@gmail.com', 'wrong', 403),
    (None, 'kadam', 422),
    ('swati@gmail.com', None, 422)
])
def test_incorrect_login(client, test_user, email, password, status_code):
    res = client.post("/login", {"username":email, "password": password})
    assert res.status_code == status_code
    # assert res.json().get('detail') == "Invalid Credentials"
