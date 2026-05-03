.PHONY: precheck setup-dev lint format test typecheck clean

precheck:
	uv run python-template precheck

setup-dev: precheck
	uv sync --all-groups
	uv run python scripts/dev_register.py
	uv run python scripts/setup_hooks.py

lint: precheck
	uv run ruff check .

format: precheck
	uv run ruff format .

test: precheck
	uv run pytest --cov=python_template --cov-report=term-missing

typecheck: precheck
	uv run mypy src scripts

clean: precheck
	rm -rf .pytest_cache .ruff_cache .mypy_cache .coverage htmlcov
	find src tests scripts -type d -name "__pycache__" -exec rm -rf {} +
