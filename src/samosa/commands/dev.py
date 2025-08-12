"""Development and testing commands."""

import click

from samosa.utils import AliasedGroup, invoked


@click.group(cls=AliasedGroup)
def dev():
    """Development and testing commands."""


@dev.command(
    name="test",
    context_settings={"ignore_unknown_options": True, "allow_extra_args": True},
)
@invoked
def test(c, cctx):
    """Run tests with pytest (proxy all arguments to pytest)."""
    from pathlib import Path

    cmd = ["pytest"]

    if not cctx.args:
        test_dirs = ["tests", "test"]
        for test_dir in test_dirs:
            if Path(test_dir).exists():
                cmd.append(test_dir)
                break
    else:
        cmd.extend(cctx.args)

    cmd_str = " ".join(cmd)
    click.echo(f"Running: {cmd_str}")

    c.run(cmd_str, pty=True)


@dev.command(name="format")
@click.option("--check", is_flag=True, help="Check formatting without making changes")
@invoked
def format_cmd(c, _, check):
    """Format code with black."""
    cmd = "black ."
    if check:
        cmd += " --check"
    c.run(cmd)


@dev.command(name="lint")
@click.option("--fix", is_flag=True, help="Fix linting issues automatically")
@invoked
def lint(c, cctx, fix):
    """Lint code with ruff."""
    cmd = "ruff check ."
    if fix:
        cmd += " --fix"
    c.run(cmd)


@dev.command(name="mypy")
@invoked
def mypy(c, cctx):
    """Run type checking with mypy."""
    c.run("mypy src/")


dev.add_command_with_aliases(format_cmd, name="format", aliases=["fmt"])
