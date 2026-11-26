from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="LIBRARY_",
        extra="ignore",
    )

    app_name: str = Field(default="LibraryAgent", min_length=1)
    environment: Literal["local", "test", "production"] = "local"
    debug: bool = False

    db_host: str = Field(default="localhost", min_length=1)
    db_port: int = Field(default=5433, ge=1, le=65535)
    db_name: str = Field(default="shop_agent", min_length=1)
    db_user: str = Field(default="shop_local_admin", min_length=1)
    db_password: SecretStr = Field(min_length=1)

    db_pool_size: int = Field(default=5, ge=1)
    db_max_overflow: int = Field(default=10, ge=0)
    db_pool_timeout: float = Field(default=30.0, gt=0)
    db_connect_timeout: int = Field(default=10, ge=2)

    @property
    def database_url(self) -> URL:
        return URL.create(
            drivername="postgresql+psycopg",
            username=self.db_user,
            password=self.db_password.get_secret_value(),
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
        )


@lru_cache
def get_settings() -> Settings:
    """Load and validate the LibraryAgent settings.

    The first successful call caches the instance.
    Subsequent calls within the same process reuse that instance.

    Args:
        None.

    Returns:
        Settings: Validated settings derived from environment variables,
            the `.env` file, and default values.

    Raises:
        pydantic.ValidationError: If a required field such as
            `LIBRARY_DB_PASSWORD` is missing or a value violates its constraints.
    """
    return Settings()
