from fastapi import FastAPI

from app.core.config import settings
from app.core.errors import register_exception_handlers
from app.modules.catalog.router import category_router, router as catalog_router

app = FastAPI(title=settings.app_name, version=settings.app_version)
register_exception_handlers(app)
app.include_router(catalog_router)
app.include_router(category_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/version")
async def version() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }