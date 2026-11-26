from collections.abc import AsyncIterator

from fastapi import Request
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import Settings


class Database:
    def __init__(self, settings: Settings) -> None:
        self.engine = create_async_engine(
            settings.database_url,
            pool_pre_ping=True,
            pool_size=settings.db_pool_size,
            max_overflow=settings.db_max_overflow,
            pool_timeout=settings.db_pool_timeout,
            connect_args={
                "connect_timeout": settings.db_connect_timeout,
            },
        )

        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )

    async def close(self) -> None:
        await self.engine.dispose()


def get_database(request: Request) -> Database:
    """Get the Database instance registered with the application.

    Args:
        request: FastAPI request that provides access to `app.state`.

    Returns:
        Database: The instance stored in `request.app.state.database`.

    Raises:
        RuntimeError: If `app.state.database` is missing or its value is not
            an instance of `Database`.
    """
    database = getattr(request.app.state, "database", None)

    if not isinstance(database, Database):
        raise RuntimeError("Database has not been initialized")

    return database


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    """Provide an asynchronous database session for the request.

    The session closes when the `async with` block exits, even if an exception
    occurs. Code that modifies the database must commit its changes.

    Args:
        request: FastAPI request used to retrieve the `Database` instance.

    Yields:
        AsyncSession: A session the request handler can use to query or modify
            the database.

    Raises:
        RuntimeError: If `get_database` cannot find a `Database` instance in
            the application state.
    """
    database = get_database(request)

    async with database.session_factory() as session:
        yield session
