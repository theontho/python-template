from python_template.main import main


def test_main_runs() -> None:
    """Basic test to ensure main can be called."""
    # This just checks it doesn't crash on import/call
    # In a real app, you might mock console or check output
    assert main() is None
