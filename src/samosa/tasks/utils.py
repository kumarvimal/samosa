"""Utility and helper tasks."""

from invoke import task


@task
def hello(ctx, name="World"):
    """Say hello to someone.

    Args:
        name: Name to greet (default: World)
    """
    print(f"Hello, {name}!")


@task
def info(ctx):
    """Show project information."""
    print("Samosa CLI Tool")
    print("Version: 0.1.0")
    print("A Python CLI tool with invoke integration")


@task
def env(ctx):
    """Show environment information."""
    import platform
    import sys

    print(f"Python version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Working directory: {ctx.cwd}")
