# Python Template

A best-practice Python project template extracted from recent successful projects.

## Features

- **Tooling:** [uv](https://github.com/astral-sh/uv) for dependency management and project isolation.
- **Code Quality:** [Ruff](https://github.com/astral-sh/ruff) for linting and formatting, [Mypy](https://github.com/python/mypy) for static type checking.
- **Testing:** [Pytest](https://github.com/pytest-dev/pytest) with `pytest-asyncio` support.
- **Structure:** Modern `src/` layout.
- **Agent Friendly:** Includes `AGENTS.md`, `GEMINI.md`, and `CLAUDE.md` for AI-assisted development.
- **CI/CD:** GitHub Actions workflow for automated checks.

## Getting Started

1.  **Clone the repository.**
2.  **Install dependencies:**
    ```bash
    uv sync
    ```
3.  **Run the application:**
    ```bash
    uv run python-template
    ```
4.  **Run tests:**
    ```bash
    uv run pytest
    ```

## Development

- **Formatting:** `uv run ruff format .`
- **Linting:** `uv run ruff check .`
- **Type Checking:** `uv run mypy src`
- **Scratch Space:** Use the `scratch/` directory for local experiments (gitignored).
- **Temporary Output:** Use `tmp/` or `out/` for logs and artifacts (gitignored).

## Configuration

Settings are managed in `pyproject.toml`.
