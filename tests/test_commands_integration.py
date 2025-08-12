"""Integration tests for samosa commands."""

import pytest

from samosa.commands.dev import dev
from samosa.commands.git import git
from samosa.commands.utils import utils
from samosa.plugins import get_local_command_group


# Git Commands Tests
@pytest.mark.integration
def test_git_help(cli_runner):
    """Test git command help."""
    result = cli_runner.invoke(git, ["--help"])

    assert result.exit_code == 0
    assert "Git version control" in result.output
    assert "status" in result.output
    assert "backup (b)" in result.output
    assert "worktree (w)" in result.output


@pytest.mark.integration
def test_backup_help(cli_runner):
    """Test backup subcommand help."""
    result = cli_runner.invoke(git, ["backup", "--help"])

    assert result.exit_code == 0
    assert "Backup branch management" in result.output
    assert "add" in result.output
    assert "list" in result.output
    assert "delete" in result.output


@pytest.mark.integration
def test_worktree_help(cli_runner):
    """Test worktree subcommand help."""
    result = cli_runner.invoke(git, ["worktree", "--help"])

    assert result.exit_code == 0
    assert "Git worktree management" in result.output
    assert "add" in result.output
    assert "list" in result.output
    assert "remove" in result.output


@pytest.mark.integration
def test_git_status_mock(cli_runner):
    """Test git status command help."""
    result = cli_runner.invoke(git, ["status", "--help"])

    assert result.exit_code == 0
    assert "Show git status" in result.output


@pytest.mark.integration
def test_git_add_mock(cli_runner):
    """Test git add command help."""
    result = cli_runner.invoke(git, ["add", "--help"])

    assert result.exit_code == 0
    assert "Add files to git staging" in result.output


# Dev Commands Tests
@pytest.mark.integration
def test_dev_help(cli_runner):
    """Test dev command help."""
    result = cli_runner.invoke(dev, ["--help"])

    assert result.exit_code == 0
    assert "Development" in result.output
    assert "lint" in result.output
    assert "test" in result.output
    assert "format" in result.output


@pytest.mark.integration
def test_dev_lint_mock(cli_runner):
    """Test dev lint command with mocked context."""
    # Just test that the command structure is correct
    result = cli_runner.invoke(dev, ["lint", "--help"])

    assert result.exit_code == 0
    assert "--fix" in result.output


@pytest.mark.integration
def test_dev_check_help(cli_runner):
    """Test dev check command help."""
    result = cli_runner.invoke(dev, ["check", "--help"])

    assert result.exit_code == 0
    assert "--fast" in result.output
    assert "--fix" in result.output


# Utils Commands Tests
@pytest.mark.integration
def test_utils_help(cli_runner):
    """Test utils command help."""
    result = cli_runner.invoke(utils, ["--help"])

    assert result.exit_code == 0
    assert "Utility" in result.output
    assert "info" in result.output
    assert "env" in result.output


@pytest.mark.integration
def test_utils_info(cli_runner):
    """Test utils info command."""
    result = cli_runner.invoke(utils, ["info"])

    assert result.exit_code == 0
    assert "CLI Tool" in result.output
    assert "Version:" in result.output


@pytest.mark.integration
def test_utils_env(cli_runner):
    """Test utils env command."""
    result = cli_runner.invoke(utils, ["env"])

    assert result.exit_code == 0
    assert "Python version:" in result.output
    assert "Platform:" in result.output


# Local Commands Tests
@pytest.mark.integration
def test_local_group_no_project(cli_runner, tmp_path, monkeypatch):
    """Test local group when no project exists."""
    monkeypatch.chdir(tmp_path)

    local = get_local_command_group()
    result = cli_runner.invoke(local, ["--help"])

    assert result.exit_code == 0
    assert "no .samosa directory found" in result.output.lower()
    assert "init" in result.output


@pytest.mark.integration
def test_local_init_command(cli_runner, tmp_path, monkeypatch):
    """Test local init command creates proper structure."""
    monkeypatch.chdir(tmp_path)

    local = get_local_command_group()
    result = cli_runner.invoke(local, ["init"])

    assert result.exit_code == 0
    assert "Initialized .samosa directory" in result.output

    # Check created structure
    assert (tmp_path / ".samosa").exists()
    assert (tmp_path / ".samosa" / "commands").exists()
    assert (tmp_path / ".samosa" / "commands" / "__init__.py").exists()
    assert (tmp_path / ".samosa" / "commands" / "example.py").exists()
    assert (tmp_path / ".samosa" / "config.yaml").exists()


@pytest.mark.integration
def test_local_with_project(
    cli_runner, samosa_project_dir, sample_command_file, monkeypatch
):
    """Test local group with existing project."""
    monkeypatch.chdir(samosa_project_dir)

    local = get_local_command_group()
    result = cli_runner.invoke(local, ["--help"])

    assert result.exit_code == 0
    # Should show discovered commands
    assert "deploy" in result.output
    assert "test" in result.output


@pytest.mark.integration
def test_local_command_execution(
    cli_runner, samosa_project_dir, sample_command_file, monkeypatch
):
    """Test executing a project-specific command."""
    monkeypatch.chdir(samosa_project_dir)

    local = get_local_command_group()
    result = cli_runner.invoke(local, ["test"])

    assert result.exit_code == 0
    assert "Running project tests" in result.output


@pytest.mark.integration
def test_local_nested_command_execution(
    cli_runner, samosa_project_dir, sample_command_file, monkeypatch
):
    """Test executing a nested project-specific command."""
    monkeypatch.chdir(samosa_project_dir)

    local = get_local_command_group()
    result = cli_runner.invoke(local, ["deploy", "app", "dev"])

    assert result.exit_code == 0
    assert "Deploying Test Project to dev" in result.output
