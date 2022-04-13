import os
from datetime import datetime, timedelta, time
from enum import Enum
from typing import Optional
from uuid import UUID

from fastapi import FastAPI, Query, Path, Body, Header
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

    class Config:
        schema_extra = {
            "example": {
                "name": "Foo",
                "description": "A very nice Item",
                "price": 35.4,
                "tax": 3.2
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
    url: HttpUrl = Field(..., example="https://example.com")
    name: str = Field(..., example="image name")


@app.get("/user_agent/")
async def read_user_agent(user_agent: Optional[str] = Header(None)):
    return {"User-Agent": user_agent}


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
async def update_item(
        item_id: int,
        item: Item = Body(
            ...,
            examples={
                "normal": {
                    "summary": "A normal example",
                    "description": "A **normal** item works correctly.",
                    "value": {
                        "name": "Foo",
                        "description": "A very nice Item",
                        "price": 35.4,
                        "tax": 3.2,
                    },
                },
                "converted": {
                    "summary": "An example with converted data",
                    "description": "FastAPI can convert price `strings` to actual `numbers` automatically",
                    "value": {
                        "name": "Bar",
                        "price": "35.4",
                    },
                },
                "invalid": {
                    "summary": "Invalid data is rejected with an error",
                    "value": {
                        "name": "Baz",
                        "price": "thirty five point four",
                    },
                },
            },
        )
):
    results = {"item_id": item_id, "item": item}
    return results


@app.post("/items/{item_id}")
async def create_item(
    item_id: UUID,
    start_datetime: Optional[datetime] = Body(None),
    end_datetime: Optional[datetime] = Body(None),
    repeat_at: Optional[time] = Body(None),
    process_after: Optional[timedelta] = Body(None),
):
    start_process = start_datetime + process_after
    duration = end_datetime - start_process
    return {
        "item_id": item_id,
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "repeat_at": repeat_at,
        "process_after": process_after,
        "start_process": start_process,
        "duration": duration,
    }


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
