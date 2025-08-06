"""Development-focused tasks for code quality and testing."""

from pathlib import Path

from invoke import task


def get_python_paths():
    """Get paths to check for Python code."""
    paths = ["src/"]
    if Path("tests").exists():
        paths.append("tests/")
    return " ".join(paths)


@task
def lint(ctx):
    """Run code linting with ruff."""
    print("Running ruff linter...")
    paths = get_python_paths()
    ctx.run(f"ruff check {paths}")


@task
def format(ctx):
    """Format code with black and ruff."""
    print("Formatting code...")
    paths = get_python_paths()
    ctx.run(f"black {paths}")
    ctx.run(f"ruff format {paths}")


@task
def typecheck(ctx):
    """Run type checking with mypy."""
    print("Running type checker...")
    ctx.run("mypy src/")


@task
def test(ctx, coverage=True):
    """Run tests with pytest.

    Args:
        coverage: Run with coverage report (default: True)
    """
    if not Path("tests").exists():
        print("No tests directory found. Skipping tests.")
        return

    cmd = "pytest"
    if not coverage:
        cmd += " --no-cov"
    print(f"Running tests: {cmd}")
    ctx.run(cmd)


@task(pre=[lint, typecheck])
def check(ctx):
    """Run all code quality checks."""
    print("All development checks completed!")
