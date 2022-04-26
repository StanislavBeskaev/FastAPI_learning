from fastapi import FastAPI, Request
from loguru import logger

app = FastAPI()


@app.get("/items/{item_id}")
def read_root(item_id: str, request: Request):
    client_host = request.client.host
    logger.debug(f"request: {request.__dict__}")
    logger.debug(f"{request.headers=}")
    return {"client_host": client_host, "item_id": item_id}
