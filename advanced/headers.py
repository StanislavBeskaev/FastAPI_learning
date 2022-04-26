from fastapi import FastAPI, Header
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

app = FastAPI()

CUSTOM_HEADER = "X-Cat-Dog"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=[CUSTOM_HEADER]
)


# можно делать так тоже
# @app.get("/headers-and-object/")
# def get_headers(response: Response):
#     response.headers["X-Cat-Dog"] = "alone in the world"
#     return {"message": "Hello World"}

@app.get("/headers/")
def get_headers():
    content = {"message": "Hello World"}
    headers = {CUSTOM_HEADER: "alone in the world", "Content-Language": "en-US"}
    return JSONResponse(content=content, headers=headers)


@app.get("/read_headers")
def read_headers(custom_header: str = Header(..., alias="CUSTOM_HEADER")):
    logger.debug(f"{custom_header=}")

    return {"message": "Continue"}
