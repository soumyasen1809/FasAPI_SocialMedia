from fastapi.testclient import TestClient
from app.main import app
from app import schemas
from jose import jwt
import pytest
from app.config import settings


@pytest.fixture(scope="function")
def client():
    # Using yield, we can run our code before we run our test
    yield TestClient(app)   # yield is same as return
    # And here, run our code after our test finishes

    # So we can do something like,
    # before yield statement, we can create a test table
    # and after yield, we can drop those test tables


# Create a new test user here
@pytest.fixture
def test_user(client):
    user_data = {"email": "LoginTest6@email.com",
                 "password": "pass123", "name": "Login Test 6"}
    res = client.post("/users", json=user_data)

    assert res.status_code == 201

    new_user = res.json()
    new_user['password'] = user_data['password']
    return new_user


# For pytest to work automatically, name the Python file with prefix test_
# For pytest to work automatically, use prefix test_ as testing method name
# To run the pytest, run: pytest -v -s
# where -v: verbose and -s: print to the console
def test_root(client):
    res = client.get("/")
    assert res.json().get('message') == 'Hello World, Welcome to FastAPI'
    assert res.status_code == 200


def test_login_user(client, test_user):
    res = client.post(
        "/login", json={"email": test_user['email'], "password": test_user['password']})
    # The above login is different from video
    # They used form-data with "username"
    # I am using json with "email"

    login_res = schemas.Token(**res.json())
    # Validate the token here
    payload = jwt.decode(login_res.access_token,
                         settings.secret_key, [settings.algorithm])
    id: str = payload.get("user_id")
    assert id == test_user['id']
    assert login_res.token_type == "bearer"

    assert res.status_code == 200



# def test_incorrect_login(client, test_user):
#     res = client.post("/login", json={"email": "wrongemail@email.com", "password": "Wrong password"})

#     assert res.status_code == 403
#     assert res.json().get('detail') == f"Invalid credentials for the email wrongemail@email.com"

