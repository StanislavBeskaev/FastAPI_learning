from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # или можно указать ['*']
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/index")
async def main():
    return {"message": "Hello World"}
