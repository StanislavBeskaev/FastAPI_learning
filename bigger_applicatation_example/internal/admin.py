import json
import os
import secrets
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from loguru import logger
from pydantic import BaseModel

router = APIRouter()
security = HTTPBasic()

ADMINS_FILE = os.path.join(Path(__file__).resolve().parent, "admins.json")


class Admin(HTTPBasicCredentials):
    def __str__(self):
        return f"{self.username}/{self.password}"


class AdminList(BaseModel):
    admins: list[Admin]


def compare(first, second):
    return secrets.compare_digest(first, second)


def check_auth(credentials: HTTPBasicCredentials = Depends(security)) -> Admin:
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


class AdminHandler:
    __instance = None
    admins_list: AdminList = AdminList.parse_file(ADMINS_FILE)

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            logger.debug("Создан instance AdminHandler")
            cls.__instance = super().__new__(cls)
        else:
            logger.debug("AdminHandler взят из __instance")

        return cls.__instance

    @classmethod
    def get_admin_list(cls) -> AdminList:
        logger.debug(f"{cls.__name__}: get_admin_list")
        return cls.admins_list

    @classmethod
    def get_admins(cls) -> list[Admin]:
        logger.debug(f"{cls.__name__}: get_admins")
        return cls.admins_list.admins

    @classmethod
    def get_admin_by_username(cls, username: str) -> Admin:
        for admin in cls.admins_list.admins:
            if admin.username == username:
                return admin

    @classmethod
    def add_admin(cls, new_admin: Admin) -> None:
        if cls.get_admin_by_username(new_admin.username):
            raise HTTPException(status_code=409, detail=f"Admin with username '{new_admin.username}' already exist")

        cls.admins_list.admins.append(new_admin)
        cls._save_admin_list()
        logger.debug(f"Добавлен новый админ: {new_admin}")

    @classmethod
    def delete_admin_by_username(cls, username: str) -> None:
        if not cls.get_admin_by_username(username=username):
            raise HTTPException(status_code=400, detail=f"Admin with username: {username} not exist")

        admins = list(filter(lambda admin: admin.username != username, cls.admins_list.admins))
        cls.admins_list.admins = admins
        cls._save_admin_list()
        logger.debug(f"Удалён админ: {username}")

    @classmethod
    def _save_admin_list(cls) -> None:
        with open(ADMINS_FILE, mode="w") as file:
            json.dump(obj=cls.admins_list.dict(), fp=file, indent=2, ensure_ascii=False)


@router.post(
    "/",
    dependencies=[Depends(check_auth)]
)
async def create_admin(new_admin: Admin):
    AdminHandler.add_admin(new_admin)
    return {"message": f"Created new admin: {new_admin.username}"}


@router.get("/username")
def read_admin_username(username: str = Depends(get_current_admin_username)):
    logger.debug(f"Пользователь {username} запросил имя пользователя")
    return {"admin": username}


@router.get("/")
async def admins_list():
    return [{"username": admin.username} for admin in AdminHandler.get_admins()]


@router.delete(
    "/",
    dependencies=[Depends(check_auth)]
)
async def delete_admin_by_name(username: str):
    AdminHandler.delete_admin_by_username(username)
    return {"message": f"Admin '{username}' deleted"}
