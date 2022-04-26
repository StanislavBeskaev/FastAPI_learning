import json
import os
import secrets
from pathlib import Path

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from loguru import logger
from pydantic import parse_file_as

security = HTTPBasic()

ADMINS_FILE = os.path.join(Path(__file__).resolve().parent, "admins.json")


class Admin(HTTPBasicCredentials):
    def __str__(self):
        return f"{self.username}/{self.password}"


def parse_admins() -> list[Admin]:
    logger.warning("parse_admins")
    return parse_file_as(list[Admin], ADMINS_FILE)


class AdminHandler:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            logger.info("Создан instance AdminHandler")
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        if not hasattr(self, "_admin_list"):
            self._admin_list = parse_admins()

    def get_admins(self) -> list[Admin]:
        logger.debug(f"{self.__class__.__name__}: get_admins")
        return self._admin_list[:]

    def add_admin(self, new_admin: Admin) -> None:
        if self._get_admin_by_username(new_admin.username):
            raise HTTPException(status_code=409, detail=f"Admin with username '{new_admin.username}' already exist")

        self._admin_list.append(new_admin)
        logger.debug(f"Добавлен новый админ: {new_admin}")

    def delete_admin_by_username(self, username: str) -> None:
        if not self._get_admin_by_username(username=username):
            raise HTTPException(status_code=400, detail=f"Admin with username: {username} not exist")

        self._admin_list = list(filter(lambda admin: admin.username != username, self._admin_list))
        logger.debug(f"Удалён админ: {username}")

    def _get_admin_by_username(self, username: str) -> Admin:
        for admin in self._admin_list:
            if admin.username == username:
                return admin

    def save_admin_list(self) -> None:
        with open(ADMINS_FILE, mode="w") as file:
            json.dump(obj=[admin.dict() for admin in self._admin_list], fp=file, indent=2, ensure_ascii=False)
        logger.debug(f"admin_list saved")


def compare(first, second):
    return secrets.compare_digest(first, second)


def check_auth(credentials: HTTPBasicCredentials = Depends(security)) -> Admin:
    logger.debug(f"check_auth credentials: {credentials}")
    current_admin = None

    for admin in AdminHandler().get_admins():
        if compare(credentials.username, admin.username) and compare(credentials.password, admin.password):
            current_admin = admin
            break

    if not current_admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return current_admin


def get_current_admin_username(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    username = check_auth(credentials).username
    logger.debug(f"Пользователь {username} запросил имя пользователя")
    return username
