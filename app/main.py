from fastapi import FastAPI

from app.core.config import settings
from app.modules.actions.routes import router as action_router
from app.modules.conditions.routes import router as condition_router
from app.modules.engine.routes import router as engine_router
from app.modules.evaluations.routes import router as evaluation_router
from app.modules.rules.routes import router as rule_router
from app.modules.users.routes import router as user_router


def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.app.app_name,
        version="1.0.0",
        debug=settings.app.debug,
    )

    application.include_router(condition_router, prefix="/api/v1")
    application.include_router(action_router, prefix="/api/v1")
    application.include_router(rule_router, prefix="/api/v1")
    application.include_router(evaluation_router, prefix="/api/v1")
    application.include_router(engine_router, prefix="/api/v1")
    application.include_router(user_router, prefix="/api/v1")

    @application.get("/health", tags=["health"])
    async def health_check() -> dict[str, str]:
        return {"status": "ok"}

    return application


app = create_application()
