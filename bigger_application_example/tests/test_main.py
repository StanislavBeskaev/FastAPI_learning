from .base_test_class import BaseTestCase


class TestMain(BaseTestCase):
    def test_main(self):
        response = self.client.get("/", params=self.valid_params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Hello Bigger Applications!"})