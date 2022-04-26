from fastapi import FastAPI, Cookie
from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import BaseModel

app = FastAPI()

SUPER_COOKIE = "fakesession"
VALID_COOKIE_VALUE = "fake-cookie-session-value"


class Message(BaseModel):
    message: str


@app.post("/cookie_and_object")
def create_cookie():
    """Установка cookie"""
    content = {"message": "Come to the dark side, we have cookies"}
    response = JSONResponse(content=content)
    response.set_cookie(key=SUPER_COOKIE, value=VALID_COOKIE_VALUE)
    response.status_code = 202
    return response


@app.get("/check_cookie", response_model=Message)
def check_cookie(cookie: str = Cookie(..., alias=SUPER_COOKIE)):
    logger.debug(f"{cookie=}")
    if cookie != VALID_COOKIE_VALUE:
        return JSONResponse(Message(message="Wrong cookie").dict(), status_code=400)

    return {"message": "Cookie accepted"}
