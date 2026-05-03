.PHONY: setup-dev lint format test typecheck clean

setup-dev:
	uv sync --all-groups
	uv run python scripts/dev_register.py
	uv run python scripts/setup_hooks.py

lint:
	uv run ruff check .

format:
	uv run ruff format .

test:
	uv run pytest --cov=python_template --cov-report=term-missing

typecheck:
	uv run mypy src scripts

clean:
	rm -rf .pytest_cache .ruff_cache .mypy_cache .coverage htmlcov
	find src tests scripts -type d -name "__pycache__" -exec rm -rf {} +
