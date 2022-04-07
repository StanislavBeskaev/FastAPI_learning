import os
from enum import Enum
from typing import Optional

from fastapi import FastAPI, Query
from pydantic import BaseModel

app = FastAPI()
fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None


class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


q_param = Query(..., max_length=50, min_length=1,  description="кушка")
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


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item, q: str | None = None):
    item_dict = item.dict()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})

    result = {"item_id": item_id, **item_dict}
    if q:
        result.update({"q": q})
    return result


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
