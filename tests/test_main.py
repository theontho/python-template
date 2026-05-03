import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from python_template.main import main, run_precheck


def test_precheck_passes(tmp_config_dir: Path) -> None:
    """Ensure the pre-check logic works."""
    tmp_config_dir.mkdir(parents=True, exist_ok=True)
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


def test_main_config_show_redacts_api_key(
    capsys: pytest.CaptureFixture[str], tmp_config_dir: Path
) -> None:
    """Test 'config show' does not expose secret-like values."""
    (tmp_config_dir / "config.toml").write_text('api_key = "secret-value"\n')

    with patch.object(sys, "argv", ["python-template", "config", "show"]):
        main()

    captured = capsys.readouterr()
    assert "api_key" in captured.out
    assert "<redacted>" in captured.out
    assert "secret-value" not in captured.out


def test_main_run_greeting(capsys: pytest.CaptureFixture[str], tmp_config_dir: None) -> None:
    """Test the 'run' command with a custom name."""
    with patch.object(sys, "argv", ["python-template", "run", "--name", "Alice"]):
        main()

    captured = capsys.readouterr()
    assert "Hello, Alice" in captured.out


def test_main_cli_overrides_config_data_dir(
    capsys: pytest.CaptureFixture[str], tmp_config_dir: Path, tmp_path: Path
) -> None:
    """Command-line flags override config.toml values."""
    configured_data_dir = tmp_path / "configured-data"
    cli_data_dir = tmp_path / "cli-data"
    (tmp_config_dir / "config.toml").write_text(f'data_dir = "{configured_data_dir}"\n')

    with patch.object(
        sys,
        "argv",
        ["python-template", "--data-dir", str(cli_data_dir), "run"],
    ):
        main()

    captured = capsys.readouterr()
    assert "cli-data" in captured.out
    assert str(configured_data_dir) not in captured.out


def test_main_config_init(tmp_config_dir: Path) -> None:
    """Test 'config init' command."""
    config_path = tmp_config_dir / "config.toml"
    if config_path.exists():
        config_path.unlink()

    with patch.object(sys, "argv", ["python-template", "config", "init"]):
        main()

    assert config_path.exists()


def test_main_config_init_force(tmp_config_dir: Path) -> None:
    """Test 'config init --force' command."""
    config_path = tmp_config_dir / "config.toml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text("initial content")

    # Without --force, it shouldn't overwrite
    with patch.object(sys, "argv", ["python-template", "config", "init"]):
        main()
    assert config_path.read_text() == "initial content"

    # With --force, it should overwrite
    with patch.object(sys, "argv", ["python-template", "config", "init", "--force"]):
        main()
    assert config_path.read_text() != "initial content"
    assert "log_level" in config_path.read_text()


def test_main_config_init_force_repairs_invalid_config(tmp_config_dir: Path) -> None:
    """Force init can replace invalid TOML config."""
    config_path = tmp_config_dir / "config.toml"
    config_path.write_text("log_level = [\n")

    with patch.object(sys, "argv", ["python-template", "config", "init", "--force"]):
        main()

    assert "log_level" in config_path.read_text()


def test_main_config_init_honors_cli_overrides(tmp_config_dir: Path, tmp_path: Path) -> None:
    """Config init writes command-line overrides, not environment values."""
    data_dir = tmp_path / "configured-data"

    with patch.object(
        sys,
        "argv",
        ["python-template", "--log-level", "DEBUG", "--data-dir", str(data_dir), "config", "init"],
    ):
        main()

    config_text = (tmp_config_dir / "config.toml").read_text()
    assert 'log_level = "DEBUG"' in config_text
    assert str(data_dir) in config_text


def test_main_quiet(capsys: pytest.CaptureFixture[str], tmp_config_dir: None) -> None:
    """Test the --quiet flag."""
    with patch.object(sys, "argv", ["python-template", "--quiet", "run"]):
        main()

    captured = capsys.readouterr()
    assert "Starting python-template..." not in captured.err
    assert "Hello, World" not in captured.out


def test_main_rich_markup_is_escaped(
    capsys: pytest.CaptureFixture[str], tmp_config_dir: None
) -> None:
    """User-provided values are rendered literally, not as Rich markup."""
    with patch.object(sys, "argv", ["python-template", "run", "--name", "[red]Alice[/red]"]):
        main()

    captured = capsys.readouterr()
    assert "[red]Alice[/red]" in captured.out
    assert "Hello, Alice" not in captured.out


def test_main_debug_overrides_config_log_level(
    capsys: pytest.CaptureFixture[str], tmp_config_dir: Path
) -> None:
    """Debug flag overrides config.toml log level."""
    (tmp_config_dir / "config.toml").write_text('log_level = "ERROR"\n')

    with patch.object(sys, "argv", ["python-template", "--debug", "run"]):
        main()

    captured = capsys.readouterr()
    assert "Debug logging is enabled" in captured.out


def test_main_log_level_overrides_config(
    capsys: pytest.CaptureFixture[str], tmp_config_dir: Path
) -> None:
    """Explicit log level flag overrides config.toml log level."""
    (tmp_config_dir / "config.toml").write_text('log_level = "ERROR"\n')

    with patch.object(sys, "argv", ["python-template", "--log-level", "DEBUG", "run"]):
        main()

    captured = capsys.readouterr()
    assert "Debug logging is enabled" in captured.out


def test_main_interrupt(capsys: pytest.CaptureFixture[str], tmp_config_dir: None) -> None:
    """Test KeyboardInterrupt handling."""
    with patch.object(sys, "argv", ["python-template", "run"]):
        with patch("python_template.main.get_config", side_effect=KeyboardInterrupt):
            with pytest.raises(SystemExit) as e:
                main()
            assert e.value.code == 130

    captured = capsys.readouterr()
    assert "Interrupted by user." in captured.out
