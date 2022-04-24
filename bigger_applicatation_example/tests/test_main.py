from .base_test_class import BaseTestCase


class TestMain(BaseTestCase):
    def test_main(self):
        response = self.client.get("/", params={"token": self.valid_token})
        assert response.status_code == 200
        assert response.json() == {"message": "Hello Bigger Applications!"}
