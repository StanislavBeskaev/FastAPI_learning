import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from loguru import logger

app = FastAPI()


client_requests = []


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()

    logger.debug("middleware before await")
    response = await call_next(request)
    logger.debug("middleware after await")

    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)

    logger.debug("send response")
    return response


@app.middleware("http")
async def add_some_header(request: Request, call_next):
    response = await call_next(request)
    if response.status_code == 200:
        logger.debug("add some header")
        response.headers["X-some"] = "thing"

    return response


@app.exception_handler(ValueError)
def handle_wrong_pk(request: Request, exc: ValueError):
    logger.debug("handle_wrong_pk")
    response = JSONResponse(content={"message": "pk must be one"}, status_code=400)
    return response


@app.get("/some/{pk}")
def some(pk: int):
    if pk != 1:
        raise ValueError("pk is not one!")
    logger.debug(f"request to /some")
    return {"some": "thing"}
