import time

from fastapi import FastAPI, Request
from loguru import logger

app = FastAPI()


client_requests = []


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()

    logger.debug("middleware before await")
    logger.debug(f"{request.__dict__=}")
    response = await call_next(request)
    logger.debug("middleware after await")

    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)

    logger.debug("send response")
    return response


@app.get("/some")
def some():
    logger.debug(f"request to /some")
    return {"some": "thing"}
