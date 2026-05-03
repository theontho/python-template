.PHONY: lint format test typecheck clean

lint:
	uv run ruff check .

format:
	uv run ruff format .

test:
	uv run pytest --cov=python_template --cov-report=term-missing

typecheck:
	uv run mypy src

clean:
	rm -rf .pytest_cache .ruff_cache .mypy_cache .coverage htmlcov
	find . -type d -name "__pycache__" -exec rm -rf {} +
