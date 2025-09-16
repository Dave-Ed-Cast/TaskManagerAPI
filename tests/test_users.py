from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_user():
    response = client.post("/users/register", json={"username": "alice", "password": "secret"})
    assert response.status_code == 200
