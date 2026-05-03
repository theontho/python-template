import sys
from unittest.mock import patch

import pytest

from python_template.main import main, run_precheck


def test_precheck_passes() -> None:
    """Ensure the pre-check logic works."""
    # This should pass in the current environment
    assert run_precheck() is True


def test_main_cli_help(capsys: pytest.CaptureFixture[str]) -> None:
    """Test that the CLI help works."""
    with patch.object(sys, "argv", ["python-template", "--help"]):
        with pytest.raises(SystemExit) as e:
            main()
        assert e.value.code == 0

    captured = capsys.readouterr()
    assert "usage: python-template" in captured.out
    assert "{precheck,config,run}" in captured.out


def test_main_version(capsys: pytest.CaptureFixture[str]) -> None:
    """Test the --version flag."""
    with patch.object(sys, "argv", ["python-template", "--version"]):
        with pytest.raises(SystemExit) as e:
            main()
        assert e.value.code == 0

    captured = capsys.readouterr()
    assert "python-template" in captured.out


def test_main_config_show(capsys: pytest.CaptureFixture[str], tmp_config_dir: None) -> None:
    """Test 'config show' command."""
    with patch.object(sys, "argv", ["python-template", "config", "show"]):
        main()

    captured = capsys.readouterr()
    assert "Configuration" in captured.out
    assert "log_level" in captured.out


def test_main_run_greeting(capsys: pytest.CaptureFixture[str], tmp_config_dir: None) -> None:
    """Test the 'run' command with a custom name."""
    with patch.object(sys, "argv", ["python-template", "run", "--name", "Alice"]):
        main()

    captured = capsys.readouterr()
    assert "Hello, Alice" in captured.out


def test_main_interrupt(capsys: pytest.CaptureFixture[str], tmp_config_dir: None) -> None:
    """Test KeyboardInterrupt handling."""
    with patch.object(sys, "argv", ["python-template", "run"]):
        with patch("python_template.main.get_config", side_effect=KeyboardInterrupt):
            with pytest.raises(SystemExit) as e:
                main()
            assert e.value.code == 130

    captured = capsys.readouterr()
    assert "Interrupted by user." in captured.out
