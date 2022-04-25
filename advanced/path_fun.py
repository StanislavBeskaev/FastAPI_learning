from fastapi import FastAPI

app = FastAPI()


@app.get("/items/", include_in_schema=False)  # так этот endpoint не будет показан в документации
async def read_items():
    return [{"item_id": "Foo"}]


@app.get("/main/", openapi_extra={"x-aperture-labs-portal": "blue"})
async def main():
    """
        Main endpoint, just for test
    """
    return {"message": "Hello from main"}
