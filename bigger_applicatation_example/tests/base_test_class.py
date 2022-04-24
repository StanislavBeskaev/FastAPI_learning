from fastapi.testclient import TestClient

from ..main import app


class BaseTestCase:
    client = TestClient(app)
    valid_token = "jessica"
