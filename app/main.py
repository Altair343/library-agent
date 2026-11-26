from fastapi import FastAPI

from app.api.health import router as health_router
from app.core.config import Settings, get_settings


def create_app(settings: Settings | None = None) -> FastAPI:
    config = settings if settings is not None else get_settings()

    application = FastAPI(
        title=config.app_name,
        debug=config.debug and config.environment == "local",
    )

    application.include_router(health_router)

    return application
