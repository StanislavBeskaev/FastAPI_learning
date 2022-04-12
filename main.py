import os
from enum import Enum
from typing import Optional

from fastapi import FastAPI, Query, Path, Body
from pydantic import BaseModel, Field

app = FastAPI()
fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


class Item(BaseModel):
    name: str
    description: Optional[str] = Field(
        None, title="The description of the item", max_length=300
    )
    price: float = Field(..., gt=0, description="The price must be greater than zero")
    tax: Optional[float] = Field(None, description="Tax is not required")


class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


@app.get("/items/{item_id}")
async def read_items(
        *,
        item_id: int = Path(..., description="The ID of the item to get", gt=0, lt=1000),
        q: str,
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results


q_param = Query(..., max_length=50, min_length=1, description="кушка")

q_list_default = Query(
    ["ку", "ку", "шка"],
    min_length=1,
    description="кушка",
    alias="item-query",
    # include_in_schema=False   # так не будет показываться в документации
)


@app.get("/")
def hello():
    return {"Hello": "World"}


@app.get("/items/")
async def read_items(q: list[str] = q_list_default):
    query_items = {"q": q}
    return query_items


@app.post("/items/")
async def create_item(item: Item):  # тут item будет в body и проверяться по модели Item
    item_dict = item.dict()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})

    return item_dict


class User(BaseModel):
    username: str
    full_name: Optional[str] = None


@app.put("/items/{item_id}")
async def update_item(
    *,
    item_id: int,
    item: Item,  # модель должна быть в Body
    user: User,  # модель должна быть в Body
    importance: int = Body(..., gt=0),
    q: Optional[str] = None
):
    results = {"item_id": item_id, "item": item, "user": user, "importance": importance}
    if q:
        results.update({"q": q})
    return results


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
