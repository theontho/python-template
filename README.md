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
    ```bash
    uv run python-template config init
    ```
5.  **Setup Development Environment:**
    ```bash
    uv run python scripts/dev_register.py   # Register your git identity
    uv run python scripts/setup_hooks.py    # Install git hooks
    ```
    `dev_register.py` prefers the active `gh` account as the default identity when GitHub CLI is logged in. In non-interactive environments, it uses that default automatically. Use `--choice N` to select a specific listed identity. The script writes `.dev_id` and updates this repository's local `git config user.name` and `git config user.email` to match; pass `--no-update-git-config` to only write `.dev_id`.
6.  **Run the application:**
    ```bash
    uv run python-template run
    ```
7.  **Run tests:**
    ```bash
    uv run pytest
    ```

## Global Installation

You can install this template globally as a tool:
```bash
uv tool install .
```

To smoke-test a built wheel in a separate uv-managed virtual environment:
```bash
uv build
uv venv /tmp/python-template-smoke
uv pip install --python /tmp/python-template-smoke/bin/python dist/python_template-0.1.0-py3-none-any.whl
/tmp/python-template-smoke/bin/python-template --version
```

## Configuration

Configuration is stored in `config.toml` under the platform-standard app config directory. On macOS, existing `~/.config` directories are preferred; otherwise the platform default is used. Configuration comes only from `config.toml` and command-line arguments, with command-line arguments taking precedence.

You can view the current configuration with:
```bash
python-template config show
```

Runtime overrides are available as CLI flags:
```bash
python-template --log-level DEBUG --data-dir /tmp/python-template-data run
```
