from collections.abc import Generator
from pathlib import Path
from unittest.mock import patch

import pytest

import python_template.config as config_module


@pytest.fixture
def tmp_config_dir(tmp_path: Path) -> Generator[Path, None, None]:
    """Provide a temporary directory for configuration files."""
    with patch("python_template.config.get_config_dir", return_value=tmp_path):
        config_module._config = None
        yield tmp_path
        config_module._config = None
