import sys
import tomllib
from pathlib import Path
from typing import Any, Literal

import tomli_w
from platformdirs import user_config_dir, user_data_dir
from pydantic import BaseModel, ConfigDict, Field, field_validator

APP_NAME = "python-template"
APP_AUTHOR = "theontho"
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class ConfigLoadError(RuntimeError):
    """Raised when config.toml cannot be loaded."""


def get_config_dir() -> Path:
    """Get the standard user configuration directory for this app."""
    # Priority for macOS: Use ~/.config/APP_NAME/ if ~/.config exists
    if sys.platform == "darwin":
        dot_config = Path.home() / ".config"
        if dot_config.is_dir():
            return dot_config / APP_NAME

    return Path(user_config_dir(APP_NAME, APP_AUTHOR))


def get_config_path() -> Path:
    """Get the path to the config.toml file."""
    return get_config_dir() / "config.toml"


class AppConfig(BaseModel):
    """Application configuration managed by config.toml."""

    model_config = ConfigDict(extra="ignore")

    log_level: LogLevel = Field(default="INFO", description="Logging level")
    data_dir: Path = Field(
        default_factory=lambda: Path(user_data_dir(APP_NAME, APP_AUTHOR)),
        description="Directory for data storage",
    )
    api_key: str | None = Field(default=None, description="Optional API key")

    @field_validator("log_level", mode="before")
    @classmethod
    def normalize_log_level(cls, value: Any) -> Any:
        if isinstance(value, str):
            return value.upper()
        return value

    @classmethod
    def load(cls) -> "AppConfig":
        """Load configuration from config.toml."""
        config_path = get_config_path()
        data = {}

        if config_path.exists():
            try:
                with config_path.open("rb") as f:
                    data = tomllib.load(f)
            except (OSError, tomllib.TOMLDecodeError) as e:
                raise ConfigLoadError(
                    f"Could not load config from {config_path}: {e}. "
                    "Run 'python-template config init --force' to replace it with defaults."
                ) from e

        return cls(**data)

    def save(self) -> None:
        """Save current configuration to the TOML file."""
        config_path = get_config_path()
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # TOML doesn't support None/null, so we exclude those fields
        data = self.model_dump(mode="json", exclude_none=True)

        with open(config_path, "wb") as f:
            tomli_w.dump(data, f)


_config: AppConfig | None = None


def get_config(reload: bool = False) -> AppConfig:
    """
    Get the global application configuration.

    Note: This returns a global singleton. In multi-threaded or async contexts,
    modifying this object may require additional synchronization.
    """
    global _config
    if _config is None or reload:
        _config = AppConfig.load()
    return _config
