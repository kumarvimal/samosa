"""Build and release focused tasks."""

from invoke import task


@task
def clean(ctx):
    """Clean build artifacts and cache files."""
    print("Cleaning build artifacts...")
    ctx.run("rm -rf build/ dist/ *.egg-info/")
    ctx.run("rm -rf .pytest_cache/ .mypy_cache/ .ruff_cache/")
    ctx.run("rm -rf htmlcov/ .coverage coverage.xml")
    ctx.run("find . -type d -name __pycache__ -exec rm -rf {} +", warn=True)


@task
def build(ctx):
    """Build the package."""
    print("Building package...")
    ctx.run("python3 -m build")


@task(pre=[clean])
def release(ctx):
    """Prepare for release: clean, check, test, and build."""
    from .development import check, test

    print("Running release preparation...")

    # Run checks and tests
    check(ctx)
    test(ctx)

    # Build the package
    build(ctx)
    print("Release preparation completed!")
