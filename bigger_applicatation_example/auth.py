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
    return parse_file_as(list[Admin], ADMINS_FILE, )


class AdminHandler:
    __instance = None
    _admin_list: list[Admin] = parse_admins()

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            logger.debug("Создан instance AdminHandler")
            cls.__instance = super().__new__(cls)
        else:
            logger.debug("AdminHandler взят из __instance")

        return cls.__instance

    @classmethod
    def get_admins(cls) -> list[Admin]:
        logger.debug(f"{cls.__name__}: get_admins")
        return cls._admin_list

    @classmethod
    def add_admin(cls, new_admin: Admin) -> None:
        if cls._get_admin_by_username(new_admin.username):
            raise HTTPException(status_code=409, detail=f"Admin with username '{new_admin.username}' already exist")

        cls._admin_list.append(new_admin)
        cls._save_admin_list()
        logger.debug(f"Добавлен новый админ: {new_admin}")

    @classmethod
    def delete_admin_by_username(cls, username: str) -> None:
        if not cls._get_admin_by_username(username=username):
            raise HTTPException(status_code=400, detail=f"Admin with username: {username} not exist")

        admins = list(filter(lambda admin: admin.username != username, cls._admin_list))
        cls._admin_list = admins
        cls._save_admin_list()
        logger.debug(f"Удалён админ: {username}")

    @classmethod
    def _get_admin_by_username(cls, username: str) -> Admin:
        for admin in cls._admin_list:
            if admin.username == username:
                return admin

    @classmethod
    def _save_admin_list(cls) -> None:
        with open(ADMINS_FILE, mode="w") as file:
            json.dump(obj=[admin.dict() for admin in cls._admin_list], fp=file, indent=2, ensure_ascii=False)
        logger.debug(f"admin_list saved")


def compare(first, second):
    return secrets.compare_digest(first, second)


def check_auth(credentials: HTTPBasicCredentials = Depends(security)) -> Admin:
    logger.debug(f"credentials: {credentials}")
    current_admin = None

    for admin in AdminHandler.get_admins():
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
    return check_auth(credentials).username
