from fastapi.testclient import TestClient

from ..main import app

client = TestClient(app)


def test_main():
    response = client.get("/?token=jessica", )
    assert response.status_code == 200
    assert response.json() == {"message": "Hello Bigger Applications!"}
