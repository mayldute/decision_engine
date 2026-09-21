from fastapi import FastAPI

from app.core.config import settings
from app.modules.conditions.routers import router as condition_router


def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.app.app_name,
        version="1.0.0",
        debug=settings.app.debug,
    )

    application.include_router(condition_router, prefix="/api/v1")

    @application.get("/health", tags=["health"])
    async def health_check() -> dict[str, str]:
        return {"status": "ok"}

    return application


app = create_application()
