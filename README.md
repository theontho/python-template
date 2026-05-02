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
3.  **Run pre-check:**
    ```bash
    uv run python-template precheck
    ```
4.  **Initialize config:**
7.  **Register dev identity:**
    ```bash
    uv run python-template dev-register
    ```
    ```bash
    uv run python-template config init
    ```
5.  **Run the application:**
    ```bash
    uv run python-template run
    ```
6.  **Run tests:**
    ```bash
    uv run pytest
    ```

## Global Installation

You can install this template globally as a tool:
```bash
uv tool install .
```

## Configuration

Configuration is stored in a platform-standard directory (e.g., `~/.config/python-template/config.toml` on macOS/Linux). You can view the current configuration with:
```bash
python-template config show
```

