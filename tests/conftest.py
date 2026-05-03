import os
from collections.abc import Generator
from pathlib import Path
from unittest.mock import patch

import pytest


@pytest.fixture
def tmp_config_dir(tmp_path: Path) -> Generator[Path, None, None]:
    """Provide a temporary directory for configuration files."""
    with patch("python_template.config.get_config_dir", return_value=tmp_path):
        yield tmp_path


@pytest.fixture
def env_override() -> Generator[None, None, None]:
    """Allow overriding environment variables for testing."""
    old_env = dict(os.environ)
    yield
    os.environ.clear()
    os.environ.update(old_env)
