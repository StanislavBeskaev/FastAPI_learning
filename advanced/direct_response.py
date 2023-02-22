import os
import datetime
from pathlib import Path

from fastapi import FastAPI, Response
from fastapi.responses import (
    HTMLResponse,
    RedirectResponse,
    PlainTextResponse,
    StreamingResponse,
    FileResponse,
)

from loguru import logger

app = FastAPI()


@app.get("/legacy/")
def get_legacy_data():
    data = """<?xml version="1.0"?>
    <shampoo>
    <Header>
        Apply shampoo here.
    </Header>
    <Body>
        You'll have to use soap here.
    </Body>
    </shampoo>
    """
    return Response(content=data, media_type="application/xml")


@app.get("/items/", response_class=HTMLResponse)  # благодаря этому в документации будет указан Media type: text/html
async def read_items():
    return """
    <html>
        <head>
            <title>Some HTML in here</title>
        </head>
        <body>
            <h1>Look ma! HTML!</h1>
        </body>
    </html>
    """


@app.get("/redirect")
async def redirect(key: int):
    if key == 3:
        return RedirectResponse(url="/legacy/")
    return {"key": key}


@app.get("/fastapi", response_class=RedirectResponse, status_code=302)
async def redirect_fastapi():
    return "https://fastapi.tiangolo.com"  # магия response_class, redirect на указанный uri


@app.get("/", response_class=PlainTextResponse)
async def main():
    return "Hello World"


async def fake_video_streamer():
    for i in range(10):
        yield f"some fake video bytes {i}".encode()


@app.get("/stream")
async def stream():
    return StreamingResponse(fake_video_streamer())


video_file = os.path.join(Path(__file__).resolve().parent, "video", "1may2021.mp4")


@app.get("/video")
def video():
    def iterfile():
        with open(video_file, mode="rb") as file_like:
            logger.debug(f"return video {datetime.datetime.now()}")
            yield from file_like

    return StreamingResponse(iterfile(), media_type="video/mp4")


@app.get("/video_file", response_class=FileResponse)
async def get_video_file():
    return video_file


@app.get("/cookie")
async def wanna_cookie(response: Response):
    """Wanna some cookie?"""
    response.set_cookie(key="token", value="secret token info", expires=20, httponly=True)
    response.set_cookie(key="public", value="some public info", expires=200)
    return {"message": "cookie for all!"}
