import os
from pathlib import Path

from python_template.config import AppConfig, get_config


def test_config_load_default(tmp_config_dir: Path) -> None:
    """Test loading default configuration."""
    config = AppConfig.load()
    assert config.log_level == "INFO"
    # data_dir is now platform-dependent, so we check if it's a Path
    assert isinstance(config.data_dir, Path)


def test_config_save_and_load(tmp_config_dir: Path) -> None:
    """Test saving and then loading configuration."""
    config = AppConfig(log_level="DEBUG", api_key="test-key")
    config.save()

    config_path = tmp_config_dir / "config.toml"
    assert config_path.exists()

    loaded_config = AppConfig.load()
    assert loaded_config.log_level == "DEBUG"
    assert loaded_config.api_key == "test-key"


def test_config_env_override(tmp_config_dir: Path, env_override: None) -> None:
    """Test environment variable overrides."""
    os.environ["APP_LOG_LEVEL"] = "WARNING"
    os.environ["APP_API_KEY"] = "env-key"

    config = AppConfig.load()
    assert config.log_level == "WARNING"
    assert config.api_key == "env-key"


def test_get_config_singleton(tmp_config_dir: Path) -> None:
    """Test that get_config returns a singleton."""
    config1 = get_config(reload=True)
    config2 = get_config()
    assert config1 is config2
