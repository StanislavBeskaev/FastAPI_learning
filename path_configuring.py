from typing import Optional, Set

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from loguru import logger
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None
    tags: Set[str] = set()


@app.post("/items/", response_model=Item, tags=["items"], summary="Create an item")
async def create_item(item: Item):
    """
        Create an item with all the information:

        - **name**: each item must have a name
        - **description**: a long description
        - **price**: required
        - **tax**: if the item doesn't have tax, you can omit this
        - **tags**: a set of unique tag strings for this item
        """
    return item


@app.get("/items/", tags=["items"])
async def read_items():
    return [{"name": "Foo", "price": 42}]


@app.get("/users/", tags=["users"])
async def read_users():
    return [{"username": "johndoe"}]


fake_db = {}


@app.put("/items/{item_id}")
def update_item(item_id: str, item: Item):
    logger.debug(f"update item with id {item_id} new data: {item}")

    json_compatible_item_data = jsonable_encoder(item)
    logger.debug(f"{json_compatible_item_data=}")

    fake_db[item_id] = json_compatible_item_data
    logger.debug(f"new db is: {fake_db}")

    return {"current_db": fake_db}
