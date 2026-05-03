import argparse
import os
import sys
import tempfile
from collections.abc import Iterable
from pathlib import Path

from rich.console import Console
from rich.markup import escape
from rich.table import Table

from python_template import __version__
from python_template.config import AppConfig, get_config, get_config_path
from python_template.log import get_logger, setup_logging

# Initialize global console and logger
console = Console()
log = get_logger("python-template")


def run_precheck() -> bool:
    """Check if the environment and dependencies are correctly set up."""
    console.print("[bold blue]Running Pre-check...[/bold blue]")
    all_passed = True

    # Example check: Python version
    py_version = sys.version_info
    if py_version.major < 3 or (py_version.major == 3 and py_version.minor < 12):
        log.error(f"Python 3.12+ required, found {sys.version}")
        all_passed = False
    else:
        log.info(f"Python version {sys.version.split()[0]} OK")

    # Example check: Config directory writable
    config_path = get_config_path()
    try:
        config_dir = config_path.parent
        if config_dir.exists():
            fd, test_path = tempfile.mkstemp(prefix=".write-test-", dir=config_dir)
            os.close(fd)
            Path(test_path).unlink(missing_ok=True)
            log.info(f"Config directory {config_dir} is writable")
        else:
            parent_dir = config_dir.parent
            if (
                parent_dir.exists()
                and parent_dir.is_dir()
                and os.access(parent_dir, os.W_OK | os.X_OK)
            ):
                log.info(f"Config directory parent {parent_dir} is writable")
            else:
                log.error(f"Config directory parent {parent_dir} is not writable")
                all_passed = False
    except Exception as e:
        log.error(f"Config directory {config_path.parent} is NOT writable: {e}")
        all_passed = False

    if all_passed:
        console.print("[bold green]Pre-check passed![/bold green]")
    else:
        console.print("[bold red]Pre-check failed![/bold red]")

    return all_passed


def redacted_config_items(config: AppConfig) -> Iterable[tuple[str, str]]:
    """Yield display-safe config key/value pairs."""
    for key, value in config.model_dump().items():
        if any(secret_part in key.lower() for secret_part in ("key", "token", "secret")):
            yield key, "<redacted>" if value else "None"
        else:
            yield key, str(value)


def apply_cli_overrides(config: AppConfig, args: argparse.Namespace) -> AppConfig:
    """Apply explicit command-line overrides on top of config.toml values."""
    updates: dict[str, object] = {}
    if args.log_level is not None:
        updates["log_level"] = args.log_level
    if args.data_dir is not None:
        updates["data_dir"] = args.data_dir
    return config.model_copy(update=updates)


def handle_config(args: argparse.Namespace, config: AppConfig) -> None:
    """Handle the 'config' subcommand."""
    config_path = get_config_path()

    if args.action == "show":
        table = Table(title=f"Configuration ({escape(str(config_path))})")
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="magenta")

        for key, value in redacted_config_items(config):
            table.add_row(key, escape(value))

        console.print(table)
    elif args.action == "init":
        if config_path.exists() and not args.force:
            log.warning(f"Config file already exists at {config_path}. Use --force to overwrite.")
        else:
            config.save()
            log.info(f"Initialized default config at {config_path}")


def main() -> None:
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(
        description="Best-practice Python project template CLI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--quiet", action="store_true", help="Suppress all output except errors")
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Override the configured logging level",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        help="Override the configured data directory",
    )

    subparsers = parser.add_subparsers(dest="command", help="Subcommands")

    # Precheck subcommand
    subparsers.add_parser("precheck", help="Check environment and dependencies")

    # Config subcommand
    config_parser = subparsers.add_parser("config", help="Manage configuration")
    config_parser.add_argument("action", choices=["show", "init"], help="Config action to perform")
    config_parser.add_argument(
        "--force", action="store_true", help="Force overwrite when initializing"
    )

    # Example 'run' subcommand
    run_parser = subparsers.add_parser("run", help="Run the main application logic")
    run_parser.add_argument("--name", default="World", help="Name to greet")

    args = parser.parse_args()

    # Load config and setup logging
    try:
        if args.command == "config" and args.action == "init":
            config = AppConfig()
        else:
            config = get_config()
        config = apply_cli_overrides(config, args)
        log_level = "ERROR" if args.quiet else "DEBUG" if args.debug else config.log_level
        setup_logging(level=log_level)

        if args.command == "precheck":
            if not run_precheck():
                sys.exit(1)
        elif args.command == "config":
            handle_config(args, config)
        elif args.command == "run" or args.command is None:
            if args.command is None:
                log.info("No command specified, defaulting to 'run'")

            log.debug("Debug logging is enabled")
            log.info("Starting python-template...")
            name = getattr(args, "name", "World")
            if not args.quiet:
                console.print(
                    f"[bold green]Hello, {escape(name)} from python-template![/bold green]"
                )
                console.print(f"Data directory: [cyan]{escape(str(config.data_dir))}[/cyan]")
        else:
            parser.print_help()
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user.[/yellow]")
        sys.exit(130)
    except Exception as e:
        log.exception(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
