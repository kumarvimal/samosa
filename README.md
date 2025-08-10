# Samosa CLI

A Python-based utility CLI tool with project-specific plugin support because I don't want to write bash scripts anymore.

> Tl;DR: Usage example
> 
> ```bash
>  python3 -m pip install -e . --break-system-packages # global install
>  samosa --help
>  samosa u install-alias
>  s --help
>  s g --help
>  s g worktree add feat/some-feature
>  s g backup --add  # create backup branch
>  s local init      # setup project-specific commands
>  s l deploy app staging  # run project commands
> ```

## Installation

### Install Globally

```bash
python3 -m pip install -e . --break-system-packages
```

### Install Shell Integration

```bash
# Install short alias 's' for samosa
samosa u install-alias

# Install tab completion
samosa u install-completion

# Source your shell config or restart terminal
source ~/.zshrc  # or ~/.bashrc for bash
```

## Quick Start

### Basic Usage

```bash
# Show all available commands
samosa --help

# Global command
samosa hello         # Say hello

# Development tasks
samosa dev lint      # or samosa development lint
samosa dev format    # Format code with black
samosa dev test      # Run tests
samosa dev build     # Build package
samosa dev clean     # Clean artifacts

# Git operations
samosa git status    # or samosa g status
samosa git browse    # Open repo in GitHub
samosa git sync      # Sync with remote main

# Project-specific commands
samosa local init    # Initialize .samosa directory
samosa local --help  # Show project commands
```

### Using Short Commands

After installing the alias:

```bash
# Use 's' instead of 'samosa'
s --help
s hello             # global command
s dev lint          # development lint  
s g status          # git status
s g backup --add    # create backup branch
s l --help          # show project commands
```

### Git Worktree Management

```bash
# Create new worktree for feature branch
samosa g worktree add feat/new-feature

# Create worktree from specific branch
samosa g worktree add new-feature --base main

# List all worktrees
samosa g worktree list

# Remove worktree
samosa g worktree remove feat-new-feature
```

### Git Backup Management

```bash
# Create backup branch with timestamp
samosa g backup --add

# List all backup branches for current branch
samosa g backup --list

# Delete specific backup branch
samosa g backup --delete --branch backup/main-14-30-22_08-08-2025

# Delete all backup branches (with confirmation)
samosa g backup --delete --all
```

### Project-Specific Commands

```bash
# Initialize .samosa directory in your project
samosa local init

# This creates:
# .samosa/
# ├── commands/
# │   ├── __init__.py
# │   └── example.py      # Example project commands
# └── config.yaml         # Project configuration

# Use project commands
samosa local --help       # or samosa l --help
samosa l deploy app staging
samosa l setup
samosa l test
```

## Available Commands

### Global Commands
- `hello` - Say hello (demo command)

### Command Groups

#### Git Operations (`git` / `g`)
- `status`, `add`, `commit`, `push`, `pull`, `merge`, `checkout`
- `browse` - Open current repo in GitHub
- `sync` - Sync current branch with remote main
- **Worktree Management (`worktree` / `w`)**
  - `add <branch>` - Create new worktree 
  - `list` - List all worktrees
  - `remove <branch>` - Remove worktree
- **Backup Management (`backup` / `b`)**
  - `--add` (default) - Create backup branch with timestamp
  - `--list` - List all backup branches for current branch
  - `--delete --branch <name>` - Delete specific backup branch
  - `--delete --all` - Delete all backup branches (with confirmation)

#### Development (`dev` / `development`)
- `lint` - Run code linting with ruff
- `format` - Format code with black and ruff
- `typecheck` - Run type checking with mypy
- `test` - Run tests with pytest
- `build` - Build the package
- `clean` - Clean build artifacts

#### Utils (`utils` / `u`)
- `info` - Show project information
- `env` - Show environment information
- `install-alias` - Install shell alias
- `uninstall-alias` - Remove shell alias
- `install-completion` - Install shell completion
- `uninstall-completion` - Remove shell completion

#### Local/Project Commands (`local` / `l`)
- `init` - Initialize .samosa directory in current project
- `--help` - Show project-specific commands (when .samosa exists)
- Dynamic commands loaded from `.samosa/commands/` directory

## Tab Completion

After installing completion with `samosa u install-completion`:

```bash
samosa <TAB>         # Shows all available commands
samosa g <TAB>       # Shows git commands
samosa git w<TAB>    # Completes to 'worktree'
samosa dev <TAB>     # Shows development commands
samosa l <TAB>       # Shows project commands (if .samosa exists)
s g stat<TAB>        # Completes to 'status' using alias
s l d<TAB>           # Completes project commands
```

## Configuration

### Global Configuration

Samosa uses Click for command-line parsing and Invoke for shell execution. Commands are organized in `src/samosa/commands/` with aliases defined in the main CLI.

### Project-Specific Configuration

Each project can have its own configuration in `.samosa/config.yaml`:

```yaml
# Project-specific configuration
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
```

This configuration is available to project commands via `project_context.config`.

## Development

### Project Structure

```
samosa/
├── src/samosa/
│   ├── cli.py              # Main CLI entry point with Click groups
│   ├── utils.py            # AliasedGroup and CLI utilities
│   ├── plugins.py          # Project plugin system
│   └── commands/
│       ├── __init__.py
│       ├── git.py          # Git operations
│       ├── dev.py          # Development tasks
│       ├── utils.py        # Utility commands
│       └── local.py        # Project-specific command bridge
├── pyproject.toml          # Project configuration
├── LICENSE
└── README.md
```

### Adding Global Commands

1. Create a new command module in `src/samosa/commands/`
2. Import and add to main CLI in `src/samosa/cli.py`

```python
# Example: src/samosa/commands/docker.py
import click
from invoke import Context
from ..utils import AliasedGroup

@click.group(cls=AliasedGroup)
def docker():
    """Docker container management."""
    pass

@docker.command()
@click.option("--tag", default="latest", help="Image tag")
def build(tag):
    """Build Docker image."""
    ctx = Context()
    ctx.run(f"docker build -t myapp:{tag} .")

@docker.command()
@click.option("--port", default="8000", help="Port to expose")
def run(port):
    """Run Docker container."""
    ctx = Context()
    ctx.run(f"docker run -p {port}:8000 myapp")
```

Then add to `src/samosa/cli.py`:
```python
from .commands.docker import docker
main.add_command_with_aliases(docker, name="docker", aliases=["d"])
```

### Adding Project-Specific Commands

1. Run `samosa local init` in your project
2. Add Python files to `.samosa/commands/`
3. Commands are auto-discovered and available via `samosa local`

```python
# Example: .samosa/commands/deploy.py
import click

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
    config = project_context.config
    
    click.echo(f"🚀 Deploying to {environment}...")
    click.echo(f"📁 Project: {config.get('project', {}).get('name', 'Unknown')}")
    
    # Run deployment commands
    # ctx.run(f"docker build -t myapp:{environment} .")
    click.echo(f"✅ Deployed to {environment}!")
```

## Best Practices

### Git Worktree Usage
- Use `samosa g worktree add <branch>` for clean feature development
- Worktrees are created in parent directory with format: `{project}-{branch}`
- Automatic branch fetching and tracking for existing remote branches

### Git Backup Usage
- Use `samosa g backup --add` before risky operations (rebasing, force pushing)
- Backup branches follow format: `backup/{branch}-{timestamp}`
- Use `samosa g backup --list` to see available backups
- Clean up old backups regularly with `samosa g backup --delete --all`

### Command Organization
- Global commands: Available directly (`samosa hello`)
- Command groups: Organized by functionality (`samosa dev lint`, `samosa g status`)
- Project commands: Specific to current project (`samosa l deploy`)
- Use short aliases for frequently used commands (`s g`, `s l`, etc.)

### Project Structure
- Keep project commands in `.samosa/commands/` directory
- Use meaningful filenames that reflect command purpose
- Access project context via `project_context` global variable
- Store project configuration in `.samosa/config.yaml`

### Shell Integration
- Install alias for shorter commands: `s` instead of `samosa`
- Install completion for better productivity
- Both work together: `s g <TAB>` shows git commands

## Troubleshooting

### Command Not Found
```bash
# Ensure samosa is in PATH
which samosa
# If not found, reinstall globally
python3 -m pip install -e . --break-system-packages
```

### Completion Not Working
```bash
# Reinstall completion
samosa u uninstall-completion
samosa u install-completion
# Restart terminal
exec zsh  # or exec bash
```

### Alias Not Working
```bash
# Check if alias exists
alias | grep samosa
# If not found, reinstall
samosa u install-alias
source ~/.zshrc  # or ~/.bashrc
```

### Local Commands Not Found
```bash
# Ensure you're in a project with .samosa directory
ls -la .samosa/commands/

# If not found, initialize project
samosa local init

# Check if commands are properly formatted
samosa local --help
```

### Project Context Not Available
```bash
# Ensure your command files use the project_context global
# It's automatically injected when commands are loaded

# In your .samosa/commands/*.py files:
def my_command():
    ctx = project_context.invoke_ctx  # For shell commands
    config = project_context.config   # For configuration
```

## Features

- ✅ **Click-based CLI** with rich argument parsing and validation
- ✅ **Command aliases** for shorter commands (`g` for `git`, `l` for `local`)
- ✅ **Clean help formatting** showing `command (alias)` format
- ✅ **Project plugin system** for project-specific commands
- ✅ **Git worktree management** with automatic branch tracking
- ✅ **Git backup system** with timestamp-based branch naming  
- ✅ **Shell integration** with aliases and tab completion
- ✅ **Development tools** integration (ruff, black, mypy, pytest)
- ✅ **Auto-discovery** of project commands from `.samosa/commands/`
- ✅ **Project context** with configuration and shell execution
