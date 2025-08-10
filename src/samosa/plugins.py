"""Plugin system for loading project-specific commands."""

import importlib.util
from pathlib import Path
import sys
from typing import Dict, Optional

import click
from invoke import Context

from .utils import AliasedGroup


class ProjectContext:
    """Context object providing project-specific utilities."""

    def __init__(self, project_root: Path, samosa_dir: Path):
        self.project_root = project_root
        self.samosa_dir = samosa_dir
        self.config_file = samosa_dir / "config.yaml"
        self._config = None
        self._invoke_context = None

    @property
    def config(self) -> Dict:
        """Load and cache project configuration."""
        if self._config is None:
            self._config = {}
            if self.config_file.exists():
                try:
                    import yaml

                    with open(self.config_file) as f:
                        self._config = yaml.safe_load(f) or {}
                except ImportError:
                    # yaml not available, skip config loading
                    pass
                except Exception:
                    # Config file invalid, use empty config
                    pass
        return self._config

    @property
    def invoke_ctx(self) -> Context:
        """Get invoke context with project root as working directory."""
        if self._invoke_context is None:
            self._invoke_context = Context()
            # Set working directory to project root
            self._invoke_context.cd(str(self.project_root))
        return self._invoke_context

    def run(self, command: str, **kwargs):
        """Run command in project root directory."""
        return self.invoke_ctx.run(command, **kwargs)


class ProjectCommandLoader:
    """Loads commands from project .samosa directory."""

    def __init__(self):
        self.project_root = None
        self.samosa_dir = None
        self.project_context = None

    def find_project_root(self, start_path: Optional[Path] = None) -> Optional[Path]:
        """Find project root by looking for .samosa directory."""
        if start_path is None:
            start_path = Path.cwd()

        current = start_path.resolve()

        # Walk up the directory tree
        for parent in [current, *list(current.parents)]:
            samosa_dir = parent / ".samosa"
            if samosa_dir.is_dir():
                commands_dir = samosa_dir / "commands"
                if commands_dir.is_dir():
                    return parent

        return None

    def discover_project(self) -> bool:
        """Discover and initialize project context."""
        project_root = self.find_project_root()
        if project_root is None:
            return False

        self.project_root = project_root
        self.samosa_dir = project_root / ".samosa"
        self.project_context = ProjectContext(project_root, self.samosa_dir)
        return True

    def load_commands(self) -> Dict[str, click.Command]:
        """Load all commands from .samosa/commands/ directory."""
        if not self.discover_project():
            return {}

        commands_dir = self.samosa_dir / "commands"
        commands = {}

        # Add commands directory to Python path temporarily
        if str(commands_dir) not in sys.path:
            sys.path.insert(0, str(commands_dir))

        try:
            # Scan for Python files in commands directory
            for py_file in commands_dir.glob("*.py"):
                if py_file.name.startswith("__"):
                    continue  # Skip __init__.py and __pycache__

                module_name = py_file.stem
                try:
                    # Load the module
                    spec = importlib.util.spec_from_file_location(module_name, py_file)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)

                        # Inject project_context into module globals
                        module.__dict__["project_context"] = self.project_context

                        spec.loader.exec_module(module)

                        # Look for Click groups or commands in the module
                        for attr_name in dir(module):
                            attr = getattr(module, attr_name)
                            if isinstance(attr, (click.Group, click.Command)):
                                # Use module name as command name unless it has a different name
                                command_name = (
                                    getattr(attr, "name", None) or module_name
                                )
                                commands[command_name] = attr

                except Exception as e:
                    click.echo(f"Warning: Failed to load {py_file}: {e}", err=True)
                    continue

        finally:
            # Remove commands directory from Python path
            if str(commands_dir) in sys.path:
                sys.path.remove(str(commands_dir))

        return commands

    def create_local_group(self) -> click.Group:
        """Create the 'local' command group with discovered commands."""
        if not self.discover_project():
            # No project found, return empty group
            @click.group(cls=AliasedGroup)
            def local():
                """Project-specific commands (no .samosa directory found)."""

            @local.command()
            def init():
                """Initialize .samosa directory in current project."""
                samosa_dir = Path.cwd() / ".samosa"
                commands_dir = samosa_dir / "commands"

                if samosa_dir.exists():
                    click.echo(f"✅ .samosa directory already exists at: {samosa_dir}")
                    return

                # Create directory structure
                commands_dir.mkdir(parents=True)

                # Create __init__.py
                (commands_dir / "__init__.py").write_text("")

                # Create example command
                example_command = '''"""Example project-specific commands."""
import click
from invoke import Context

# project_context is injected by the samosa plugin system
project_context = None  # type: ignore


@click.group()
def deploy():
    """Deployment commands for this project."""
    pass


@deploy.command()
@click.argument("environment", type=click.Choice(["dev", "staging", "prod"]))
def app(environment):
    """Deploy application to specified environment."""
    # Access project context
    ctx = project_context.invoke_ctx

    click.echo(f"🚀 Deploying to {environment}...")
    click.echo(f"📁 Project root: {project_context.project_root}")

    # Example: run deployment commands
    # ctx.run(f"docker build -t myapp:{environment} .")
    # ctx.run(f"kubectl apply -f k8s/{environment}/")

    click.echo(f"✅ Deployed to {environment}!")


@click.command()
def test():
    """Run project-specific tests."""
    ctx = project_context.invoke_ctx

    click.echo("🧪 Running project tests...")
    # ctx.run("python -m pytest tests/")
    click.echo("✅ Tests completed!")


@click.command()
def setup():
    """Setup project development environment."""
    ctx = project_context.invoke_ctx

    click.echo("🔧 Setting up development environment...")
    # ctx.run("pip install -r requirements.txt")
    # ctx.run("pre-commit install")
    click.echo("✅ Development environment ready!")
'''

                (commands_dir / "example.py").write_text(example_command)

                # Create optional config file
                config_content = """# Project-specific configuration
project:
  name: "My Project"
  version: "1.0.0"

environments:
  dev:
    url: "http://localhost:3000"
  staging:
    url: "https://staging.myproject.com"
  prod:
    url: "https://myproject.com"
"""
                (samosa_dir / "config.yaml").write_text(config_content)

                click.echo(f"🎉 Initialized .samosa directory at: {samosa_dir}")
                click.echo(f"📝 Example commands created in: {commands_dir}")
                click.echo(f"⚙️  Configuration file: {samosa_dir / 'config.yaml'}")
                click.echo("\n✨ Try: samosa local --help")

            return local

        # Project found, load commands
        @click.group(cls=AliasedGroup)
        def local():
            """Project-specific commands."""

        # Load and add discovered commands
        discovered_commands = self.load_commands()

        if not discovered_commands:

            @local.command()
            def info():
                """Show project information."""
                click.echo(f"📁 Project root: {self.project_root}")
                click.echo(f"⚙️  Samosa directory: {self.samosa_dir}")
                click.echo(f"📝 Commands directory: {self.samosa_dir / 'commands'}")
                click.echo(
                    "\n💡 No commands found. Add Python files to .samosa/commands/"
                )

        else:
            # Add discovered commands to local group
            for name, command in discovered_commands.items():
                local.add_command(command, name=name)

        return local


# Global loader instance
_loader = ProjectCommandLoader()


def get_local_command_group() -> click.Group:
    """Get the local command group with project-specific commands."""
    return _loader.create_local_group()
