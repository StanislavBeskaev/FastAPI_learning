import os
from enum import Enum
from typing import Optional

from fastapi import FastAPI, Query, Path, Body
from pydantic import BaseModel, Field, HttpUrl

app = FastAPI()
fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


class Tag(BaseModel):
    name: str = Field(..., max_length=50, description="Tag name")
    key: int = Field(..., gt=0, description="Key must be positive")
    url: HttpUrl

    def __hash__(self):
        return hash(f"{self.key}:{self.name}")


class Item(BaseModel):
    name: str
    description: Optional[str] = Field(
        None, title="The description of the item", max_length=300
    )
    price: float = Field(..., gt=0, description="The price must be greater than zero")
    tax: Optional[float] = Field(None, description="Tax is not required")
    tags: list[Tag]

    class Config:
        schema_extra = {
            "example": {
                "name": "Foo",
                "description": "A very nice Item",
                "price": 35.4,
                "tax": 3.2,
                "tags": [
                    {
                        "name": "tag name",
                        "key": 1,
                        "url": "https://example.com"
                    }
                ]
            }
        }


class Offer(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    items: list[Item]


class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


class Image(BaseModel):
    url: HttpUrl
    name: str


@app.post("/images/multiple/")
async def create_multiple_images(
        # images ожидается в Body как json списка Image
        images: list[Image] = Body(..., description="Изображения")
):
    return images


@app.post("/offers/")
async def create_offer(offer: Offer):
    return offer


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    results = {"item_id": item_id, "item": item}
    return results


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
