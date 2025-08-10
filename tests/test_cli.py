"""Tests for samosa.cli module."""

import pytest

from samosa.cli import get_version, main


def test_main_help(cli_runner):
    """Test that main CLI shows help correctly."""
    result = cli_runner.invoke(main, ["--help"])

    assert result.exit_code == 0
    assert "Samosa" in result.output
    assert "task automation" in result.output.lower()

    # Check that command groups are shown
    assert "git (g)" in result.output
    assert "utils (u)" in result.output
    assert "dev" in result.output
    assert "local (l)" in result.output


def test_main_version(cli_runner):
    """Test that version option works."""
    result = cli_runner.invoke(main, ["--version"])

    assert result.exit_code == 0
    assert "samosa" in result.output.lower()


def test_hello_command(cli_runner):
    """Test the hello command."""
    result = cli_runner.invoke(main, ["hello"])

    assert result.exit_code == 0
    assert "Hello, World!" in result.output


def test_hello_command_with_name(cli_runner):
    """Test the hello command with custom name."""
    result = cli_runner.invoke(main, ["hello", "--name", "Test"])

    assert result.exit_code == 0
    assert "Hello, Test!" in result.output


def test_git_alias(cli_runner):
    """Test that git alias 'g' works."""
    result = cli_runner.invoke(main, ["g", "--help"])

    assert result.exit_code == 0
    assert "Git version control" in result.output


def test_utils_alias(cli_runner):
    """Test that utils alias 'u' works."""
    result = cli_runner.invoke(main, ["u", "--help"])

    assert result.exit_code == 0
    assert "Utility" in result.output


def test_local_alias(cli_runner):
    """Test that local alias 'l' works."""
    result = cli_runner.invoke(main, ["l", "--help"])

    assert result.exit_code == 0
    # Will show either project commands or init command
    assert result.output is not None


def test_invalid_command(cli_runner):
    """Test behavior with invalid command."""
    result = cli_runner.invoke(main, ["nonexistent"])

    assert result.exit_code != 0
    assert "No such command" in result.output


def test_get_version_fallback():
    """Test that get_version returns something."""
    version = get_version()

    # Should return some string, even if it's "unknown"
    assert isinstance(version, str)
    assert len(version) > 0


@pytest.mark.slow
def test_get_version_from_pyproject():
    """Test version reading from pyproject.toml."""
    # This test might be slow as it reads from filesystem
    version = get_version()

    # Should either get the real version or "unknown"
    assert (
        version in ["unknown"]
        or version.replace(".", "").replace("-", "").replace("dev", "").isalnum()
    )
