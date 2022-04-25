from loguru import logger

from ..auth import Admin, AdminHandler
from .base_test_class import BaseTestCase


# TODO mock списка админов
class TestAdmin(BaseTestCase):
    valid_auth = ("joe", "joe")
    valid_new_admin = Admin(username="new admin", password="123")
    not_valid_new_admin = Admin(username="admin", password="admin")
    not_valid_admin_username = "not valid"
    admin_for_delete = Admin(username="for delete", password="del")

    @classmethod
    def setUpClass(cls) -> None:
        logger.info(f"{cls.__name__}: setUpClass, создаём тестового админа")
        AdminHandler.add_admin(cls.admin_for_delete)
        AdminHandler.save_admin_list()

    @classmethod
    def tearDownClass(cls) -> None:
        logger.info(f"{cls.__name__}: tearDownClass, удаляем созданного админа")
        AdminHandler.delete_admin_by_username(cls.valid_new_admin.username)
        AdminHandler.save_admin_list()

    def test_list_success(self):
        response = self.client.get("/admin/", params=self.valid_params, headers=self.valid_headers)

        self.assertEqual(response.status_code, 200)
        # TODO проверка списка

    def test_list_miss_params(self):
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 422)

    def test_username_success(self):
        response = self.client.get(
            "/admin/username",
            params=self.valid_params,
            headers=self.valid_headers,
            auth=self.valid_auth
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"admin": "joe"})

    def test_username_not_auth(self):
        response = self.client.get(
            "/admin/username"
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Not authenticated"})

    def test_create_admin_success(self):
        response = self.client.post(
            "/admin/",
            params=self.valid_params,
            headers=self.valid_headers,
            auth=self.valid_auth,
            json=self.valid_new_admin.dict()
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": f"Created new admin: {self.valid_new_admin.username}"})

    def test_create_admin_already_exist(self):
        response = self.client.post(
            "/admin/",
            params=self.valid_params,
            headers=self.valid_headers,
            auth=self.valid_auth,
            json=self.not_valid_new_admin.dict()
        )

        self.assertEqual(response.status_code, 409)
        self.assertEqual(
            response.json(),
            {"detail": f"Admin with username '{self.not_valid_new_admin.username}' already exist"}
        )

    def test_create_admin_not_auth(self):
        response = self.client.post(
            "/admin/",
            json=self.valid_new_admin.dict()
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Not authenticated"})

    def test_delete_admin_success(self):
        response = self.client.delete(
            "/admin/",
            headers=self.valid_headers,
            auth=self.valid_auth,
            params={**self.valid_params, "username": self.admin_for_delete.username}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"message": f"Admin '{self.admin_for_delete.username}' deleted"}
        )

    def test_delete_admin_not_valid_username(self):
        response = self.client.delete(
            "/admin/",
            headers=self.valid_headers,
            auth=self.valid_auth,
            params={**self.valid_params, "username": self.not_valid_admin_username}
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {"detail": f"Admin with username: {self.not_valid_admin_username} not exist"}
        )

    def test_delete_admin_wrong_auth(self):
        response = self.client.delete(
            "/admin/",
            headers=self.valid_headers,
            auth=("1", "2"),
            params={**self.valid_params, "username": self.not_valid_admin_username}
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Incorrect username or password"})

    def test_delete_admin_incorrect_token(self):
        response = self.client.delete(
            "/admin/",
            headers=self.valid_headers,
            auth=self.valid_auth,
            params={"token": "incorrect"}
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "No Jessica token provided"})

    def test_delete_admin_incorrect_x_token(self):
        response = self.client.delete(
            "/admin/",
            headers={"x-token": "incorrect"},
            auth=self.valid_auth,
            params=self.valid_params
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "X-Token header invalid"})
