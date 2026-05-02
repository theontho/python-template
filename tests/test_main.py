import pytest
from python_template.main import run_precheck


def test_precheck_passes() -> None:
    """Ensure the pre-check logic works."""
    # This should pass in the current environment
    assert run_precheck() is True


def test_main_cli_help(capsys: pytest.CaptureFixture[str]) -> None:
    """Test that the CLI help works."""
    from python_template.main import main
    import sys
    from unittest.mock import patch

    with patch.object(sys, "argv", ["python-template", "--help"]):
        with pytest.raises(SystemExit) as e:
            main()
        assert e.value.code == 0
    
    captured = capsys.readouterr()
    assert "usage: python-template" in captured.out
    assert "{precheck,config,run}" in captured.out
