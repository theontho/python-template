import pytest


@pytest.fixture
def example_fixture() -> str:
    """An example pytest fixture."""
    return "fixture_value"
