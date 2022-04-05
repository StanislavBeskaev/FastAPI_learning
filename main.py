import os
from enum import Enum
from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


class Item(BaseModel):
    name: str
    price: float
    is_offer: Optional[bool]


class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


@app.get("/")
def hello():
    return {"Hello": "World"}


@app.get("/items/")
async def read_item(skip: int, limit: int = 10):  # skip обязательный, limit не обязательный
    return fake_items_db[skip:skip + limit]


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}


@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    """Обновление элемента"""
    print(f"{item=}")
    return {"item_name": item.name, "item_id": item_id}


@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name == ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}


@app.get("/files/{file_path:path}")
async def read_file(file_path: str, encoding: str = "utf-8"):
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        return {"error": f"file '{file_path}' does not exist"}

    with open(file_path, mode="r", encoding=encoding) as file:
        content = file.read()

    return {"content": content}
