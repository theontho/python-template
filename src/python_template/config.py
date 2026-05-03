import sys
import tomllib
from pathlib import Path

import tomli_w
from platformdirs import user_config_dir
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

APP_NAME = "python-template"
APP_AUTHOR = "theontho"


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


class AppConfig(BaseSettings):
    """Application configuration managed by TOML file and environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_prefix="APP_",
    )

    log_level: str = Field(default="INFO", description="Logging level (DEBUG, INFO, etc.)")
    data_dir: Path = Field(default=Path("data"), description="Directory for data storage")
    api_key: str | None = Field(default=None, description="Optional API key")

    @classmethod
    def load(cls) -> "AppConfig":
        """Load configuration from TOML file, then environment variables."""
        config_path = get_config_path()
        data = {}

        if config_path.exists():
            try:
                with open(config_path, "rb") as f:
                    data = tomllib.load(f)
            except Exception as e:
                print(f"Warning: Error loading config from {config_path}: {e}", file=sys.stderr)

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
    """Get the global application configuration."""
    global _config
    if _config is None or reload:
        _config = AppConfig.load()
    return _config
