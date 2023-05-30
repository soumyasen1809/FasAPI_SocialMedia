from fastapi.testclient import TestClient
from app.main import app
from app import schemas

client = TestClient(app)


# For pytest to work automatically, name the Python file with prefix test_
# For pytest to work automatically, use prefix test_ as testing method name
# To run the pytest, run: pytest -v -s
# where -v: verbose and -s: print to the console
def test_root():
    res = client.get("/")
    assert res.json().get('message') == 'Hello World, Welcome to FastAPI'
    assert res.status_code == 200
