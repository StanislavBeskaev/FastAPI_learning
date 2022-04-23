from fastapi import APIRouter, Depends
from loguru import logger

from ..auth import Admin, AdminHandler, check_auth, get_current_admin_username


router = APIRouter()


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
