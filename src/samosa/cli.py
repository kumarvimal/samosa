"""CLI interface for samosa."""

import click


@click.command()
@click.version_option(version="0.1.0", prog_name="samosa")
@click.help_option("--help", "-h")
def main() -> None:
    """Samosa - A Python CLI tool."""
    click.echo("Welcome to Samosa!")


if __name__ == "__main__":
    main()