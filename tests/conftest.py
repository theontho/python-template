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
def env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    """Clean environment for testing."""
    for key in list(os.environ):
        monkeypatch.delenv(key, raising=False)
