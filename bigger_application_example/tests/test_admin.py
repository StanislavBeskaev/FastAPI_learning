from loguru import logger

from ..auth import Admin, AdminHandler
from .base_test_class import BaseTestCase


MOCK_ADMIN_LIST = [
    Admin(username="user1", password="1"),
    Admin(username="user2", password="2"),
]


class TestAdmin(BaseTestCase):
    valid_auth = (MOCK_ADMIN_LIST[0].username, MOCK_ADMIN_LIST[0].password)
    valid_new_admin = Admin(username="new admin", password="123")
    not_valid_new_admin = MOCK_ADMIN_LIST[0]
    not_valid_admin_username = "not valid"
    admin_for_delete = Admin(username="for delete", password="del")

    @classmethod
    def setUpClass(cls) -> None:
        logger.info(f"{cls.__name__}: setUpClass, добавляем admin_for_delete в MOCK_ADMIN_LIST")
        MOCK_ADMIN_LIST.append(cls.admin_for_delete)

        cls.right_admin_list = AdminHandler._admin_list[:]
        logger.info(f"{cls.__name__}: setUpClass, подменяем AdminHandler._admin_list на MOCK_ADMIN_LIST")
        AdminHandler._admin_list = MOCK_ADMIN_LIST

    @classmethod
    def tearDownClass(cls) -> None:
        logger.info(f"{cls.__name__}: tearDownClass, возвращаем AdminHandler._admin_list")
        AdminHandler._admin_list = cls.right_admin_list
        AdminHandler.save_admin_list()

    def test_list_success(self):
        right_admin_list = AdminHandler._admin_list[:]
        AdminHandler._admin_list = MOCK_ADMIN_LIST

        response = self.client.get("/admin/", params=self.valid_params, headers=self.valid_headers)

        self.assertEqual(response.status_code, 200)
        logger.debug(response.json())
        self.assertEqual(response.json(), [{"username": admin.username} for admin in MOCK_ADMIN_LIST])

        AdminHandler._admin_list = right_admin_list

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
        self.assertEqual(response.json(), {"admin": f"{self.valid_auth[0]}"})

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
