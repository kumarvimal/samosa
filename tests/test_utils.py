"""Tests for samosa.utils module."""

import click
from click.testing import CliRunner
import pytest

from samosa.utils import AliasedGroup


@pytest.fixture
def sample_group():
    """Create a sample AliasedGroup for testing."""

    @click.group(cls=AliasedGroup)
    def main():
        """Main command group."""

    @click.command()
    def test_cmd():
        """Test command."""
        click.echo("test command executed")

    @click.command()
    def another_cmd():
        """Another test command."""
        click.echo("another command executed")

    # Add commands with aliases
    main.add_command_with_aliases(test_cmd, name="test", aliases=["t"])
    main.add_command_with_aliases(another_cmd, name="another", aliases=["a", "alt"])

    return main


def test_add_command_with_aliases(sample_group):
    """Test that commands are added with proper aliases."""
    # Check that the main command is available
    assert "test" in sample_group.commands
    assert "another" in sample_group.commands

    # Check that aliases are stored
    assert "t" in sample_group._aliases
    assert "a" in sample_group._aliases
    assert "alt" in sample_group._aliases

    # Check alias mapping
    assert sample_group._aliases["t"] == "test"
    assert sample_group._aliases["a"] == "another"
    assert sample_group._aliases["alt"] == "another"


def test_get_command_with_alias(sample_group):
    """Test that get_command resolves aliases correctly."""
    # Test main command names
    test_cmd = sample_group.get_command(None, "test")
    assert test_cmd is not None
    assert test_cmd.name == "test"

    another_cmd = sample_group.get_command(None, "another")
    assert another_cmd is not None
    assert another_cmd.name == "another"

    # Test aliases
    alias_cmd = sample_group.get_command(None, "t")
    assert alias_cmd is not None
    assert alias_cmd.name == "test"

    alias_cmd2 = sample_group.get_command(None, "a")
    assert alias_cmd2 is not None
    assert alias_cmd2.name == "another"

    alias_cmd3 = sample_group.get_command(None, "alt")
    assert alias_cmd3 is not None
    assert alias_cmd3.name == "another"


def test_get_command_nonexistent(sample_group):
    """Test that get_command returns None for nonexistent commands."""
    cmd = sample_group.get_command(None, "nonexistent")
    assert cmd is None


def test_list_commands_excludes_aliases(sample_group):
    """Test that list_commands only includes main commands (not aliases)."""
    commands = sample_group.list_commands(None)

    # Should include main command names
    assert "test" in commands
    assert "another" in commands

    # Should NOT include aliases (to avoid completion duplicates)
    assert "t" not in commands
    assert "a" not in commands
    assert "alt" not in commands


def test_format_commands_shows_aliases(sample_group):
    """Test that format_commands shows clean alias format."""
    runner = CliRunner()
    result = runner.invoke(sample_group, ["--help"])

    # Check that help shows the clean format with aliases
    assert result.exit_code == 0
    help_output = result.output

    # Should show commands with aliases in parentheses
    assert "test (t)" in help_output
    assert "another (a, alt)" in help_output

    # Should not show duplicate entries
    lines = help_output.split("\n")
    test_lines = [line for line in lines if "test" in line.lower()]
    # Should only have one line with test command (not separate entries)
    command_lines = [line for line in test_lines if "test (t)" in line]
    assert len(command_lines) == 1


def test_command_execution_via_alias(sample_group):
    """Test that commands execute correctly when called via aliases."""
    runner = CliRunner()

    # Test execution via main name
    result = runner.invoke(sample_group, ["test"])
    assert result.exit_code == 0
    assert "test command executed" in result.output

    # Test execution via alias
    result = runner.invoke(sample_group, ["t"])
    assert result.exit_code == 0
    assert "test command executed" in result.output

    # Test multiple aliases
    result = runner.invoke(sample_group, ["a"])
    assert result.exit_code == 0
    assert "another command executed" in result.output

    result = runner.invoke(sample_group, ["alt"])
    assert result.exit_code == 0
    assert "another command executed" in result.output


def test_empty_aliases_list():
    """Test that commands work with empty aliases list."""

    @click.group(cls=AliasedGroup)
    def main():
        """Main command group."""

    @click.command()
    def no_alias():
        """Command without aliases."""
        click.echo("no alias command")

    main.add_command_with_aliases(no_alias, name="no-alias", aliases=[])

    runner = CliRunner()

    # Should work with main name
    result = runner.invoke(main, ["no-alias"])
    assert result.exit_code == 0
    assert "no alias command" in result.output

    # Help should show command without aliases
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "no-alias" in result.output
    # Should not show empty parentheses
    assert "no-alias ()" not in result.output


def test_single_alias():
    """Test that commands work with single alias."""

    @click.group(cls=AliasedGroup)
    def main():
        """Main command group."""

    @click.command()
    def single():
        """Command with single alias."""
        click.echo("single alias command")

    main.add_command_with_aliases(single, name="single", aliases=["s"])

    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0

    # Should show single alias format
    assert "single (s)" in result.output
