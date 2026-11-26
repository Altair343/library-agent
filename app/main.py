from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.health import router as health_router
from app.core.config import Settings, get_settings
from app.db.session import Database


def create_app(settings: Settings | None = None) -> FastAPI:
    config = settings if settings is not None else get_settings()

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncGenerator[None, None]:
        database = Database(config)
        application.state.database = database

        try:
            yield
        finally:
            await database.close()
            application.state.database = None

    app = FastAPI(
        title=config.app_name,
        debug=config.debug and config.environment == "local",
        lifespan=lifespan,
    )

    app.include_router(health_router)

    return app
