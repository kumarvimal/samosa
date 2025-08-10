"""Pytest configuration and fixtures."""

from pathlib import Path
import tempfile

from click.testing import CliRunner
import pytest
import yaml

from samosa.plugins import ProjectCommandLoader


@pytest.fixture
def cli_runner():
    """Provide a Click CLI runner for testing commands."""
    return CliRunner()


@pytest.fixture
def temp_project_dir():
    """Create a temporary project directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir) / "test_project"
        project_dir.mkdir()
        yield project_dir


@pytest.fixture
def samosa_project_dir(temp_project_dir):
    """Create a temporary project with .samosa directory structure."""
    samosa_dir = temp_project_dir / ".samosa"
    commands_dir = samosa_dir / "commands"
    commands_dir.mkdir(parents=True)

    # Create __init__.py
    (commands_dir / "__init__.py").write_text("")

    # Create config.yaml
    config = {
        "project": {"name": "Test Project", "version": "1.0.0"},
        "environments": {
            "dev": {"url": "http://localhost:3000"},
            "prod": {"url": "https://prod.example.com"},
        },
    }
    with open(samosa_dir / "config.yaml", "w") as f:
        yaml.safe_dump(config, f)

    yield temp_project_dir


@pytest.fixture
def sample_command_file(samosa_project_dir):
    """Create a sample command file in the project."""
    commands_dir = samosa_project_dir / ".samosa" / "commands"

    command_content = '''"""Sample project command for testing."""
import click

@click.group()
def deploy():
    """Deployment commands."""
    pass

@deploy.command()
@click.argument("env", type=click.Choice(["dev", "prod"]))
def app(env):
    """Deploy application."""
    config = project_context.config
    project_name = config.get("project", {}).get("name", "Unknown")
    click.echo(f"Deploying {project_name} to {env}")

@click.command()
def test():
    """Run tests."""
    click.echo("Running project tests...")
'''

    (commands_dir / "sample.py").write_text(command_content)
    return commands_dir / "sample.py"


@pytest.fixture
def project_loader():
    """Provide a ProjectCommandLoader instance."""
    return ProjectCommandLoader()


@pytest.fixture
def mock_cwd(monkeypatch, samosa_project_dir):
    """Mock the current working directory to point to our test project."""
    monkeypatch.chdir(samosa_project_dir)
    return samosa_project_dir
