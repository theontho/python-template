from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    """Application configuration managed by environment variables and .env file."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    log_level: str = Field(default="INFO", description="Logging level (DEBUG, INFO, etc.)")
    data_dir: Path = Field(default=Path("data"), description="Directory for data storage")
    api_key: str | None = Field(default=None, description="Optional API key")


def get_config() -> AppConfig:
    """Load and return the application configuration."""
    return AppConfig()
