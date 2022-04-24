from fastapi.testclient import TestClient
from unittest import TestCase

from ..main import app


class BaseTestCase(TestCase):
    client = TestClient(app)
    valid_token = "jessica"
