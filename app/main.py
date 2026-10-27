from fastapi import FastAPI

from app.core.config import settings

app = FastAPI(title = settings.app_name, version = settings.app_version)

@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/version")
async def version() -> dict[str, str]:
    return {
        "app_name": settings.app_name,
        "app_version": settings.app_version
    }

@app.get("/hello/{name}")
async def hello(name: str, shout: bool = False) -> dict[str, str]:
    message = f"Hello, {name}"
    return {'message': message.upper() if shout else message}