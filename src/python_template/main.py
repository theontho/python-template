import argparse
import sys
from importlib.metadata import version

from rich.console import Console
from rich.table import Table

from python_template.config import get_config, get_config_path
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
        config_path.parent.mkdir(parents=True, exist_ok=True)
        log.info(f"Config directory {config_path.parent} is writable")
    except Exception as e:
        log.error(f"Config directory {config_path.parent} is NOT writable: {e}")
        all_passed = False

    if all_passed:
        console.print("[bold green]Pre-check passed![/bold green]")
    else:
        console.print("[bold red]Pre-check failed![/bold red]")

    return all_passed


def handle_config(args: argparse.Namespace) -> None:
    """Handle the 'config' subcommand."""
    config = get_config()
    config_path = get_config_path()

    if args.action == "show":
        table = Table(title=f"Configuration ({config_path})")
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="magenta")

        for key, value in config.model_dump().items():
            table.add_row(key, str(value))

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
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {version('python-template')}"
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--quiet", action="store_true", help="Suppress all output except errors")

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
        config = get_config()
        log_level = "DEBUG" if args.debug else config.log_level
        setup_logging(level=log_level)

        if args.command == "precheck":
            if not run_precheck():
                sys.exit(1)
        elif args.command == "config":
            handle_config(args)
        elif args.command == "run" or args.command is None:
            if args.command is None:
                log.info("No command specified, defaulting to 'run'")

            log.debug("Debug logging is enabled")
            log.info("Starting python-template...")
            name = getattr(args, "name", "World")
            console.print(f"[bold green]Hello, {name} from python-template![/bold green]")
            console.print(f"Data directory: [cyan]{config.data_dir}[/cyan]")
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
