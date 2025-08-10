"""Integration tests for samosa commands."""

from unittest.mock import patch

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
@patch("samosa.commands.git.Context")
def test_git_status_mock(mock_context, cli_runner):
    """Test git status command with mocked context."""
    mock_ctx_instance = mock_context.return_value

    result = cli_runner.invoke(git, ["status"])

    assert result.exit_code == 0
    mock_ctx_instance.run.assert_called_once_with("git status")


@pytest.mark.integration
@patch("samosa.commands.git.Context")
def test_git_add_mock(mock_context, cli_runner):
    """Test git add command with mocked context."""
    mock_ctx_instance = mock_context.return_value

    result = cli_runner.invoke(git, ["add", "--files", "src/"])

    assert result.exit_code == 0
    mock_ctx_instance.run.assert_called_once_with("git add src/")


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
@patch("samosa.commands.dev.Context")
def test_dev_lint_mock(mock_context, cli_runner):
    """Test dev lint command with mocked context."""
    mock_ctx_instance = mock_context.return_value
    # Mock successful lint run
    mock_result = type("Result", (), {"return_code": 0})()
    mock_ctx_instance.run.return_value = mock_result

    result = cli_runner.invoke(dev, ["lint"])

    assert result.exit_code == 0
    mock_ctx_instance.run.assert_called_once_with("ruff check .", warn=True)


@pytest.mark.integration
@patch("samosa.commands.dev.Context")
def test_dev_test_mock(mock_context, cli_runner):
    """Test dev test command with mocked context."""
    mock_ctx_instance = mock_context.return_value
    # Mock successful test run
    mock_result = type("Result", (), {"return_code": 0})()
    mock_ctx_instance.run.return_value = mock_result

    result = cli_runner.invoke(dev, ["test"])

    assert result.exit_code == 0
    assert "Running: pytest tests" in result.output
    mock_ctx_instance.run.assert_called_once_with("pytest tests", warn=True)


@pytest.mark.integration
@patch("samosa.commands.dev.Context")
def test_dev_test_with_options_mock(mock_context, cli_runner):
    """Test dev test command proxies all options to pytest."""
    mock_ctx_instance = mock_context.return_value
    mock_result = type("Result", (), {"return_code": 0})()
    mock_ctx_instance.run.return_value = mock_result

    result = cli_runner.invoke(dev, ["test", "-v", "--cov=src", "-k", "test_utils"])

    assert result.exit_code == 0
    assert "Running: pytest -v --cov=src -k test_utils" in result.output
    mock_ctx_instance.run.assert_called_once_with(
        "pytest -v --cov=src -k test_utils", warn=True
    )


@pytest.mark.integration
@patch("samosa.commands.dev.Context")
def test_dev_test_failure_exit_code_mock(mock_context, cli_runner):
    """Test dev test command preserves pytest exit code on failure."""
    mock_ctx_instance = mock_context.return_value
    # Mock failed test run
    mock_result = type("Result", (), {"return_code": 1})()
    mock_ctx_instance.run.return_value = mock_result

    result = cli_runner.invoke(dev, ["test"])

    assert result.exit_code == 1
    assert "Running: pytest tests" in result.output
    mock_ctx_instance.run.assert_called_once_with("pytest tests", warn=True)


@pytest.mark.integration
@patch("samosa.commands.dev.Context")
def test_dev_format_mock(mock_context, cli_runner):
    """Test dev format command with mocked context."""
    mock_ctx_instance = mock_context.return_value
    # Mock successful format run
    mock_result = type("Result", (), {"return_code": 0})()
    mock_ctx_instance.run.return_value = mock_result

    result = cli_runner.invoke(dev, ["format"])

    assert result.exit_code == 0
    # Should call black
    mock_ctx_instance.run.assert_called_once_with("black .", warn=True)


@pytest.mark.integration
@patch("samosa.commands.dev.Context")
def test_dev_check_mock(mock_context, cli_runner):
    """Test dev check command with mocked context."""
    mock_ctx_instance = mock_context.return_value
    mock_result = type("Result", (), {"return_code": 0})()
    mock_ctx_instance.run.return_value = mock_result

    result = cli_runner.invoke(dev, ["check", "--fast"])

    assert result.exit_code == 0
    assert "🔍 Running quality checks..." in result.output
    assert "🎉 All checks passed!" in result.output
    assert "tests were skipped in fast mode" in result.output


@pytest.mark.integration
def test_dev_check_help(cli_runner):
    """Test dev check command help."""
    result = cli_runner.invoke(dev, ["check", "--help"])

    assert result.exit_code == 0
    assert "Run all quality checks" in result.output
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
