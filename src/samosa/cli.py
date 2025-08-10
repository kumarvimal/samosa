"""CLI interface for samosa using Click."""

import logging
from pathlib import Path

import click

from .commands.dev import dev
from .commands.git import git
from .commands.local import local
from .commands.utils import utils
from .utils import AliasedGroup

_logger = logging.getLogger(__name__)


def get_version():
    """Get version from package metadata or pyproject.toml."""
    try:
        # First try to get version from installed package metadata
        try:
            from importlib.metadata import version
        except ImportError:
            # Python < 3.8 fallback
            from importlib_metadata import version
        return version("samosa")
    except Exception as e:
        _logger.info("Could not get version from package metadata: %s", e)

    try:
        # Fallback: read from pyproject.toml (for development)
        import tomllib

        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent
        pyproject_path = project_root / "pyproject.toml"

        if pyproject_path.exists():
            with open(pyproject_path, "rb") as f:
                config = tomllib.load(f)
                return config.get("project", {}).get("version", "unknown")
    except Exception as e:
        _logger.warning("Could not get version from pyproject.toml: %s", e)

    return "unknown"


@click.group(cls=AliasedGroup)
@click.version_option(version=get_version(), prog_name="samosa")
def main():
    """Samosa - A Python CLI tool for task automation and project management."""


# Add command groups with aliases
main.add_command_with_aliases(git, name="git", aliases=["g"])
main.add_command_with_aliases(utils, name="utils", aliases=["u"])
main.add_command_with_aliases(dev, name="dev", aliases=["d", "development"])
main.add_command_with_aliases(local, name="local", aliases=["l"])


# Add simple hello command at root level
@main.command()
@click.option("--name", default="World", help="Name to greet")
def hello(name):
    """Say hello to someone."""
    click.echo(f"Hello, {name}!")


if __name__ == "__main__":
    main()
