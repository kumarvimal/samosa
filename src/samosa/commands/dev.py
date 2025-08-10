"""Development and testing commands."""

import click
from invoke import Context

from ..utils import AliasedGroup


@click.group(cls=AliasedGroup)
def dev():
    """Development and testing commands."""


@dev.command(
    context_settings={"ignore_unknown_options": True, "allow_extra_args": True}
)
@click.pass_context
def test(ctx):
    """Run tests with pytest (proxy all arguments to pytest)."""
    from pathlib import Path

    # Configure invoke context to not exit on command failures
    invoke_ctx = Context()

    # Base command
    cmd = ["pytest"]

    # If no args provided, default to tests directory if it exists
    if not ctx.args:
        test_dirs = ["tests", "test"]
        for test_dir in test_dirs:
            if Path(test_dir).exists():
                cmd.append(test_dir)
                break
    else:
        # Pass through all arguments to pytest
        cmd.extend(ctx.args)

    # Execute the command
    cmd_str = " ".join(cmd)
    click.echo(f"Running: {cmd_str}")

    # Run with warn=True to prevent invoke from raising exceptions on non-zero exit codes
    result = invoke_ctx.run(cmd_str, warn=True)

    # Exit with the same code pytest returned
    if result.return_code != 0:  # type: ignore
        ctx.exit(result.return_code)  # type: ignore


@dev.command(name="format")
@click.option("--check", is_flag=True, help="Check formatting without making changes")
@click.pass_context
def format_cmd(click_ctx, check):
    """Format code with black."""
    invoke_ctx = Context()
    cmd = "black ."
    if check:
        cmd += " --check"
    result = invoke_ctx.run(cmd, warn=True)
    if result.return_code != 0:  # type: ignore
        click_ctx.exit(result.return_code)  # type: ignore


@dev.command()
@click.option("--fix", is_flag=True, help="Fix linting issues automatically")
@click.pass_context
def lint(click_ctx, fix):
    """Lint code with ruff."""
    invoke_ctx = Context()
    cmd = "ruff check ."
    if fix:
        cmd += " --fix"
    result = invoke_ctx.run(cmd, warn=True)
    if result.return_code != 0:  # type: ignore
        click_ctx.exit(result.return_code)  # type: ignore


@dev.command()
@click.pass_context
def typecheck(click_ctx):
    """Run type checking with mypy."""
    invoke_ctx = Context()
    result = invoke_ctx.run("mypy src/", warn=True)
    if result.return_code != 0:  # type: ignore
        click_ctx.exit(result.return_code)  # type: ignore


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


@dev.command()
@click.option("--fast", is_flag=True, help="Skip tests for faster checking")
@click.option("--fix", is_flag=True, help="Auto-fix issues where possible")
@click.pass_context
def check(ctx, fast, fix):
    """Run all quality checks: format, lint, typecheck, and tests (exit on first failure)."""
    click.echo("🔍 Running quality checks...")
    click.echo()

    # Step 1: Format check
    click.echo("1️⃣  Checking code formatting...")
    try:
        if fix:
            ctx.invoke(format_cmd, check=False)
            click.echo("✅ Code formatted")
        else:
            ctx.invoke(format_cmd, check=True)
            click.echo("✅ Code formatting is correct")
    except SystemExit as e:
        if e.code != 0:
            click.echo("❌ Code formatting issues found")
            click.echo("💡 Run 'samosa dev check --fix' to auto-fix formatting")
            raise  # Re-raise to preserve original exit code
    except Exception as e:
        click.echo(f"❌ Format check failed: {e}")
        ctx.exit(1)

    click.echo()

    # Step 2: Lint check
    click.echo("2️⃣  Checking code with ruff...")
    try:
        ctx.invoke(lint, fix=fix)
        click.echo("✅ No linting issues found")
    except SystemExit as e:
        if e.code != 0:
            click.echo("❌ Linting issues found")
            click.echo(
                "💡 Run 'samosa dev check --fix' to auto-fix some linting issues"
            )
            raise  # Re-raise to preserve original exit code
    except Exception as e:
        click.echo(f"❌ Lint check failed: {e}")
        ctx.exit(1)

    click.echo()

    # Step 3: Type check
    click.echo("3️⃣  Checking types with mypy...")
    try:
        ctx.invoke(typecheck)
        click.echo("✅ No type errors found")
    except SystemExit as e:
        if e.code != 0:
            click.echo("❌ Type errors found")
            click.echo("💡 Run 'samosa dev typecheck' to see detailed type errors")
            raise  # Re-raise to preserve original exit code
    except Exception as e:
        click.echo(f"❌ Type check failed: {e}")
        ctx.exit(1)

    click.echo()

    # Step 4: Tests (unless --fast is used)
    if not fast:
        click.echo("4️⃣  Running tests...")
        try:
            ctx.invoke(test)
            click.echo("✅ All tests passed")
        except SystemExit as e:
            if e.code != 0:
                click.echo("❌ Tests failed")
                click.echo("💡 Run 'samosa dev test -v' for detailed test output")
                raise  # Re-raise to preserve original exit code
        except Exception as e:
            click.echo(f"❌ Test execution failed: {e}")
            ctx.exit(1)

        click.echo()
    else:
        click.echo("4️⃣  Skipping tests (--fast mode)")
        click.echo()

    # Success - all checks passed
    click.echo("🎉 All checks passed!")
    if fast:
        click.echo("   (tests were skipped in fast mode)")


# Add format command alias
dev.add_command_with_aliases(format_cmd, name="format", aliases=["fmt"])
