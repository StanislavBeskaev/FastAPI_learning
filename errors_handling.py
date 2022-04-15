from fastapi import FastAPI, HTTPException, Request, Path
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, PlainTextResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from loguru import logger


app = FastAPI()

items = {"foo": "The Foo Wrestlers"}


@app.get("/items/{item_id}")
async def read_item(item_id: str):
    if item_id not in items:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
            headers={"X-Error": "There goes my error"}
        )

    return {"item": items[item_id]}


class UnicornException(Exception):
    def __init__(self, name: str):
        self.name = name


@app.exception_handler(UnicornException)  # обработчик своего исключения
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    logger.debug(f"{request.__dict__}")
    logger.debug(f"{exc.__dict__}")
    return JSONResponse(
        status_code=418,
        content={"message": f"Oops! {exc.name} did something. There goes a rainbow..."},
    )


@app.get("/unicorns/{name}")
async def read_unicorn(name: str = Path(..., description="yolo is awesome, try it!")):
    if name == "yolo":
        raise UnicornException(name=name)
    return {"unicorn_name": name}


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return PlainTextResponse(str(exc), status_code=400)


@app.get("/books/{book_id}")
async def read_book(book_id: int = Path(..., description="number 3 is cool, you'll like it")):
    if book_id == 3:
        raise HTTPException(status_code=418, detail="Nope! I don't like 3.")
    return {"book_id": book_id}
