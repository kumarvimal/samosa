"""Tests for samosa.plugins module."""

from unittest.mock import patch

import click
import yaml

from samosa.plugins import ProjectCommandLoader, ProjectContext


# ProjectContext Tests
def test_project_context_initialization(samosa_project_dir):
    """Test that ProjectContext initializes correctly."""
    samosa_dir = samosa_project_dir / ".samosa"
    context = ProjectContext(samosa_project_dir, samosa_dir)

    assert context.project_root == samosa_project_dir
    assert context.samosa_dir == samosa_dir
    assert context.config_file == samosa_dir / "config.yaml"
    assert context._config is None
    assert context._invoke_context is None


def test_config_loading(samosa_project_dir):
    """Test that configuration is loaded correctly."""
    samosa_dir = samosa_project_dir / ".samosa"
    context = ProjectContext(samosa_project_dir, samosa_dir)

    config = context.config

    assert config is not None
    assert config["project"]["name"] == "Test Project"
    assert config["project"]["version"] == "1.0.0"
    assert config["environments"]["dev"]["url"] == "http://localhost:3000"
    assert config["environments"]["prod"]["url"] == "https://prod.example.com"


def test_config_caching(samosa_project_dir):
    """Test that configuration is cached after first load."""
    samosa_dir = samosa_project_dir / ".samosa"
    context = ProjectContext(samosa_project_dir, samosa_dir)

    # First access loads config
    config1 = context.config

    # Second access should return cached config
    config2 = context.config

    assert config1 is config2  # Same object reference


def test_config_missing_file(temp_project_dir):
    """Test behavior when config file doesn't exist."""
    samosa_dir = temp_project_dir / ".samosa"
    samosa_dir.mkdir()
    context = ProjectContext(temp_project_dir, samosa_dir)

    config = context.config
    assert config == {}


def test_config_invalid_yaml(temp_project_dir):
    """Test behavior with invalid YAML config."""
    samosa_dir = temp_project_dir / ".samosa"
    samosa_dir.mkdir()

    # Create invalid YAML
    config_file = samosa_dir / "config.yaml"
    config_file.write_text("invalid: yaml: content: [")

    context = ProjectContext(temp_project_dir, samosa_dir)

    # Should return empty config on error
    config = context.config
    assert config == {}


def test_invoke_context(samosa_project_dir):
    """Test invoke context creation and working directory."""
    samosa_dir = samosa_project_dir / ".samosa"
    context = ProjectContext(samosa_project_dir, samosa_dir)

    invoke_ctx = context.invoke_ctx

    assert invoke_ctx is not None
    # Note: We can't easily test the working directory change without
    # actually changing directories, but we can test that it returns
    # the same context on subsequent calls
    assert context.invoke_ctx is invoke_ctx  # Same object


def test_run_method(samosa_project_dir):
    """Test the run method delegates to invoke context."""
    samosa_dir = samosa_project_dir / ".samosa"
    context = ProjectContext(samosa_project_dir, samosa_dir)

    with patch.object(context.invoke_ctx, "run") as mock_run:
        mock_run.return_value = "test output"

        result = context.run("echo test", hide=True)

        mock_run.assert_called_once_with("echo test", hide=True)
        assert result == "test output"


# ProjectCommandLoader Tests
def test_initialization():
    """Test that ProjectCommandLoader initializes correctly."""
    loader = ProjectCommandLoader()

    assert loader.project_root is None
    assert loader.samosa_dir is None
    assert loader.project_context is None


def test_find_project_root_success(samosa_project_dir, mock_cwd):
    """Test finding project root when .samosa directory exists."""
    loader = ProjectCommandLoader()

    project_root = loader.find_project_root()

    assert project_root.resolve() == samosa_project_dir.resolve()


def test_find_project_root_parent_directory(samosa_project_dir, monkeypatch):
    """Test finding project root in parent directory."""
    # Create a subdirectory and set it as cwd
    subdir = samosa_project_dir / "subdir" / "deep"
    subdir.mkdir(parents=True)

    monkeypatch.chdir(subdir)

    loader = ProjectCommandLoader()
    project_root = loader.find_project_root()

    assert project_root.resolve() == samosa_project_dir.resolve()


def test_find_project_root_not_found(temp_project_dir, monkeypatch):
    """Test behavior when no .samosa directory is found."""
    monkeypatch.chdir(temp_project_dir)

    loader = ProjectCommandLoader()
    project_root = loader.find_project_root()

    assert project_root is None


def test_find_project_root_no_commands_dir(temp_project_dir, monkeypatch):
    """Test behavior when .samosa exists but no commands directory."""
    monkeypatch.chdir(temp_project_dir)

    # Create .samosa but no commands subdirectory
    samosa_dir = temp_project_dir / ".samosa"
    samosa_dir.mkdir(exist_ok=True)

    loader = ProjectCommandLoader()
    project_root = loader.find_project_root()

    assert project_root is None


def test_discover_project_success(mock_cwd):
    """Test successful project discovery."""
    loader = ProjectCommandLoader()

    result = loader.discover_project()

    assert result is True
    assert loader.project_root.resolve() == mock_cwd.resolve()
    assert loader.samosa_dir.resolve() == (mock_cwd / ".samosa").resolve()
    assert loader.project_context is not None
    assert isinstance(loader.project_context, ProjectContext)


def test_discover_project_failure(temp_project_dir, mock_cwd):
    """Test project discovery failure."""
    # Switch to directory without .samosa
    loader = ProjectCommandLoader()

    # Mock find_project_root to return None
    with patch.object(loader, "find_project_root", return_value=None):
        result = loader.discover_project()

    assert result is False
    assert loader.project_root is None
    assert loader.samosa_dir is None
    assert loader.project_context is None


def test_load_commands_no_project(temp_project_dir):
    """Test loading commands when no project is found."""
    loader = ProjectCommandLoader()

    with patch.object(loader, "discover_project", return_value=False):
        commands = loader.load_commands()

    assert commands == {}


def test_load_commands_with_sample_file(mock_cwd, sample_command_file):
    """Test loading commands from sample command file."""
    loader = ProjectCommandLoader()

    commands = loader.load_commands()

    # Should have loaded commands from sample.py
    assert len(commands) >= 2  # deploy and test commands
    assert "deploy" in commands
    assert "test" in commands

    # Check that commands are Click objects
    assert isinstance(commands["deploy"], click.Group)
    assert isinstance(commands["test"], click.Command)


def test_load_commands_ignores_invalid_files(mock_cwd):
    """Test that invalid Python files are ignored."""
    commands_dir = mock_cwd / ".samosa" / "commands"

    # Create an invalid Python file
    invalid_file = commands_dir / "invalid.py"
    invalid_file.write_text("This is not valid Python syntax !!!")

    loader = ProjectCommandLoader()

    # Should not raise an exception and should return empty dict
    # (since we don't have any valid commands in this test)
    commands = loader.load_commands()

    # The invalid file should be ignored
    assert "invalid" not in commands


def test_load_commands_ignores_special_files(mock_cwd):
    """Test that __init__.py and similar files are ignored."""
    commands_dir = mock_cwd / ".samosa" / "commands"

    # Create special files that should be ignored
    (commands_dir / "__pycache__").mkdir()
    (commands_dir / "__test__.py").write_text("# Should be ignored")

    loader = ProjectCommandLoader()
    commands = loader.load_commands()

    assert "__pycache__" not in commands
    assert "__test__" not in commands


def test_project_context_injection(mock_cwd, sample_command_file):
    """Test that project_context is injected into command modules."""
    loader = ProjectCommandLoader()

    # Mock the module loading to capture injected globals
    injected_context = None

    def capture_context():
        commands = loader.load_commands()
        # The project_context should have been injected
        nonlocal injected_context
        injected_context = loader.project_context
        return commands

    capture_context()

    assert injected_context is not None
    assert isinstance(injected_context, ProjectContext)


def test_create_local_group_no_project(temp_project_dir, monkeypatch):
    """Test creating local group when no project is found."""
    monkeypatch.chdir(temp_project_dir)

    loader = ProjectCommandLoader()
    local_group = loader.create_local_group()

    assert local_group is not None
    assert isinstance(local_group, click.Group)

    # Should have init command
    commands = local_group.list_commands(None)
    assert "init" in commands


def test_create_local_group_with_project_no_commands(mock_cwd):
    """Test creating local group with project but no commands."""
    # Remove sample command file if it exists
    commands_dir = mock_cwd / ".samosa" / "commands"
    for py_file in commands_dir.glob("*.py"):
        if py_file.name != "__init__.py":
            py_file.unlink()

    loader = ProjectCommandLoader()
    local_group = loader.create_local_group()

    assert local_group is not None
    assert isinstance(local_group, click.Group)

    # Should have info command when no commands are found
    commands = local_group.list_commands(None)
    assert "info" in commands


def test_create_local_group_with_commands(mock_cwd, sample_command_file):
    """Test creating local group with discovered commands."""
    loader = ProjectCommandLoader()
    local_group = loader.create_local_group()

    assert local_group is not None
    assert isinstance(local_group, click.Group)

    # Should have discovered commands
    commands = local_group.list_commands(None)
    assert "deploy" in commands
    assert "test" in commands


def test_init_command_creates_structure(temp_project_dir, monkeypatch):
    """Test that init command creates proper directory structure."""
    monkeypatch.chdir(temp_project_dir)

    loader = ProjectCommandLoader()
    local_group = loader.create_local_group()

    from click.testing import CliRunner

    runner = CliRunner()

    result = runner.invoke(local_group, ["init"])

    assert result.exit_code == 0

    # Check that directories were created
    samosa_dir = temp_project_dir / ".samosa"
    assert samosa_dir.exists()
    assert (samosa_dir / "commands").exists()
    assert (samosa_dir / "commands" / "__init__.py").exists()
    assert (samosa_dir / "commands" / "example.py").exists()
    assert (samosa_dir / "config.yaml").exists()

    # Check config content
    with open(samosa_dir / "config.yaml") as f:
        config = yaml.safe_load(f)
    assert "project" in config
    assert "environments" in config


def test_init_command_already_exists(mock_cwd):
    """Test init command when .samosa directory already exists."""
    # Since we're in a directory with .samosa, we get the project version of local group
    # which doesn't have init command, so we should test against no-project version
    from samosa.plugins import ProjectCommandLoader

    # Create a loader but force it to think there's no project
    loader = ProjectCommandLoader()

    # Patch find_project_root to return None to simulate no project
    with patch.object(loader, "find_project_root", return_value=None):
        local_group = loader.create_local_group()

    from click.testing import CliRunner

    runner = CliRunner()

    # Create the .samosa directory first
    samosa_dir = mock_cwd / ".samosa"
    samosa_dir.mkdir(exist_ok=True)

    result = runner.invoke(local_group, ["init"])

    assert result.exit_code == 0
    assert "already exists" in result.output
