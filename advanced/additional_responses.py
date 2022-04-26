from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel


class Item(BaseModel):
    id: str
    value: str


class Message(BaseModel):
    message: str


app = FastAPI()


@app.get(
    "/items/{item_id}",
    response_model=Item,
    responses={
        404: {
            "model": Message,
            "description": "The item was not found",
            "content": {
                "application/json": {
                    "example": {"message": "Item not found"}
                }
            }
        },
        200: {
            "description": "Item requested by ID",
            "content": {
                "application/json": {
                    "example": {"id": "bar", "value": "The bar tenders"}
                }
            },
        },
    },
)
async def read_item(item_id: str):
    """foo is cool!"""
    if item_id == "foo":
        return {"id": "foo", "value": "there goes my hero"}
    else:
        return JSONResponse(status_code=404, content={"message": "Item not found"})


@app.get(
    "/image",
    response_model=Message,
    responses={
        200: {
            "content": {"image/png": {}},
            "description": "Return the JSON item or an image.",
        }
    },
)
async def read_image(img: bool = Query(False, description="Прислать картинку?")):
    if img:
        return FileResponse("аватар.jpeg", media_type="image/png")
    else:
        return {"message": "image is interesting"}
