from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware


app = FastAPI()

# перекидывание на HTTPS и WSS
# from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
# app.add_middleware(HTTPSRedirectMiddleware)


app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["example.com", "*.example.com", "127.0.0.1"]
)


@app.get("/")
async def main():
    return {"message": "Hello World"}
