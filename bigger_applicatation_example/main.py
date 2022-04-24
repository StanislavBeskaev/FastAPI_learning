from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles

from .dependencies import get_query_token, get_token_header
from .internal import admin
from .routers import items, users, files


description = """
Bigger application API example 🚀

## Items
Получение и обновление **items**

## Users
You will be able to:
* **Get users**
* **Read users** (_not implemented_).
"""

tags_metadata = [
    {
        "name": "users",
        "description": "Operations with users. The **login** logic is also here.",
    },
    {
        "name": "items",
        "description": "Manage items. So _fancy_ they have their own docs.",
        "externalDocs": {
            "description": "Items external docs",
            "url": "https://fastapi.tiangolo.com/",
        },
    },
    {
        "name": "admin",
        "description": "Admin CRUD implementation",
    },
    {
        "name": "custom",
        "description": "I've no idea what it is"
    },
    {
        "name": "default",
        "description": "Endpoints with no tags"
    }
]

app = FastAPI(
    title="Bigger application API",
    dependencies=[Depends(get_query_token)],
    description=description,
    version="0.2.0",
    openapi_tags=tags_metadata,
    openapi_url="/api/v0.2.0/openapi.json",
    docs_url="/swagger",
    redoc_url="/redoc"
)

app.mount("/static", StaticFiles(directory="files"), name="static")

app.include_router(users.router)
app.include_router(items.router)
app.include_router(files.router)
app.include_router(
    admin.router,
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_token_header)],
    responses={418: {"description": "I'm a teapot"}},
)


@app.get("/")
async def main():
    return {"message": "Hello Bigger Applications!"}
