from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


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


@lru_cache
def get_settings() -> Settings:
    return Settings()
