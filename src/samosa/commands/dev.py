"""Development and testing commands."""
import click
from invoke import Context


@click.group()
def dev():
    """Development and testing commands."""
    pass


@dev.command()
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def test(verbose):
    """Run tests."""
    ctx = Context()
    cmd = "pytest"
    if verbose:
        cmd += " -v"
    ctx.run(cmd)


@dev.command()
@click.option("--check", is_flag=True, help="Check formatting without making changes")
def format(check):
    """Format code with black."""
    ctx = Context()
    cmd = "black ."
    if check:
        cmd += " --check"
    ctx.run(cmd)


@dev.command()
@click.option("--fix", is_flag=True, help="Fix linting issues automatically")
def lint(fix):
    """Lint code with ruff."""
    ctx = Context()
    cmd = "ruff check ."
    if fix:
        cmd += " --fix"
    ctx.run(cmd)


@dev.command()
def typecheck():
    """Run type checking with mypy."""
    ctx = Context()
    ctx.run("mypy src/")


@dev.command()
def build():
    """Build the package."""
    ctx = Context()
    ctx.run("python -m build")


@dev.command()
def clean():
    """Clean build artifacts."""
    ctx = Context()
    ctx.run("rm -rf dist/ build/ *.egg-info/")
    ctx.run("find . -type d -name __pycache__ -exec rm -rf {} +", warn=True)
    ctx.run("find . -name '*.pyc' -delete")
    click.echo("✅ Cleaned build artifacts")