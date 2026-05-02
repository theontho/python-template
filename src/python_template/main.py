import logging

from rich.console import Console
from rich.logging import RichHandler

from python_template.config import get_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)

log = logging.getLogger("python-template")
console = Console()


def main() -> None:
    """Main entry point for the application."""
    config = get_config()

    # Update log level from config
    logging.getLogger().setLevel(config.log_level)

    log.info("Starting python-template...")
    log.debug(f"Config loaded: {config}")

    console.print("[bold green]Hello from python-template![/bold green]")
    console.print(f"Data directory: [cyan]{config.data_dir}[/cyan]")


if __name__ == "__main__":
    main()
