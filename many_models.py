from typing import Optional, Union

from fastapi import FastAPI
from loguru import logger
from pydantic import BaseModel, EmailStr


app = FastAPI()


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None


class UserIn(UserBase):
    password: str


class UserOut(UserBase):
    pass


class UserInDB(UserBase):
    hashed_password: str


def fake_password_hasher(raw_password: str):
    return "supersecret" + raw_password


def fake_save_user(user_in: UserIn) -> UserInDB:
    hashed_password = fake_password_hasher(user_in.password)
    user_in_db = UserInDB(**user_in.dict(), hashed_password=hashed_password)

    logger.debug("User saved! ..not really")
    logger.debug(f"add user in db with data: {user_in_db}")

    return user_in_db


@app.post("/user/", response_model=UserOut)  # так выкинуться все лишние поля
async def create_user(user_in: UserIn):
    user_saved = fake_save_user(user_in)
    return user_saved


class BaseItem(BaseModel):
    description: str
    type: str


class CarItem(BaseItem):
    type = "car"


class PlaneItem(BaseItem):
    type = "plane"
    size: int


items = {
    "item1": {"description": "All my friends drive a low rider", "type": "car"},
    "item2": {
        "description": "Music is my aeroplane, it's my aeroplane",
        "type": "plane",
        "size": 5,
    },
}

default_item = {
    "description": "default item",
    "type": "base"
}


# FastAPI сам преобразует к нужной модели
@app.get("/items/{item_id}", response_model=Union[PlaneItem, CarItem, BaseItem])
async def read_item(item_id: str):
    return items.get(item_id, default_item)
