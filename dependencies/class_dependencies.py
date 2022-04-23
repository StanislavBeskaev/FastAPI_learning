from typing import Optional

from fastapi import Depends, FastAPI
from pydantic import BaseModel

app = FastAPI()


fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


# Можно так указать, а можно через модель
# class CommonQueryParams:
#     def __init__(self, q: Optional[str] = None, skip: int = 0, limit: int = 100):
#         self.q = q
#         self.skip = skip
#         self.limit = limit

class CommonQueryParams(BaseModel):
    q: Optional[str] = None
    skip: int = 0
    limit: int = 100
    need: int


@app.get("/items/")
async def read_items(commons: CommonQueryParams = Depends(CommonQueryParams)):
    # можно указать commons: CommonQueryParams = Depends() и тоже будет работать
    # благодаря Depends commons будет экземпляром класса CommonQueryParams
    response = {}
    if commons.q:
        response.update({"q": commons.q})
    items = fake_items_db[commons.skip:commons.skip + commons.limit]
    response.update({"items": items})
    return response
