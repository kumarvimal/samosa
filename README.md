# Samosa CLI

A python-based utility CLI tool because I don't want to write bash scripts anymore.

> Tl;DR: Usage example
> 
> ```bash
>  python3 -m pip install -e . --break-system-packages # global install
>  samosa --help
>  samosa u install-alias
>  s --help
>  s g --help
>  s g worktree add feat/some-feature
>  s g worktree remove feat/some-feature
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

# Only global command
samosa hello         # Say hello

# Development tasks (via namespace)
samosa dev lint      # or samosa development lint
samosa dev format    # Format code with black
samosa dev test      # Run tests
samosa dev check     # Run all quality checks
samosa dev typecheck # Run type checking

# Git operations (via namespace)
samosa git status    # or samosa g status
samosa git browse    # Open repo in GitHub
```

### Using Short Commands

After installing the alias:

```bash
# Use 's' instead of 'samosa'
s --help
s hello             # global command
s dev lint          # development lint  
s g status          # git status
s g browse          # open GitHub repo
```

### Git Worktree Management

```bash
# Create new worktree for feature branch
samosa g worktree add feat/new-feature

# List all worktrees
samosa g worktree list

# Remove worktree
samosa g worktree remove samosa-feat-new-feature
```

## Available Commands

### Global Commands
- `hello` - Say hello (demo command)

### Namespaced Commands

#### Git Operations (`git` / `g`)
- `status`, `add`, `commit`, `push`, `pull`, `merge`, `checkout`
- `browse` - Open current repo in GitHub
- `worktree add <branch>` - Create new worktree
- `worktree list` - List all worktrees  
- `worktree remove <name>` - Remove worktree

#### Development (`development` / `dev`)
- `lint` - Run code linting with ruff
- `format` - Format code with black and ruff
- `typecheck` - Run type checking with mypy
- `check` - Run all code quality checks
- `test` - Run tests with pytest

#### Utils (`utils` / `u`)
- `info` - Show project information
- `env` - Show environment information
- `hello` - Say hello (also available globally)
- `install-alias` - Install shell alias
- `uninstall-alias` - Remove shell alias
- `install-completion` - Install shell completion
- `uninstall-completion` - Remove shell completion

## Tab Completion

After installing completion with `samosa u install-completion`:

```bash
samosa <TAB>         # Shows all available commands
samosa g <TAB>       # Shows git namespace commands
samosa git w<TAB>    # Completes to 'worktree'
samosa dev <TAB>     # Shows development commands
s g stat<TAB>        # Completes to 'status' using alias
```

## Configuration

Task modules are auto-discovered from `src/samosa/tasks/`. Configuration is handled in `src/samosa/tasks/config.py`:

```python
TASK_CONFIGS = {
    "git": {
        "module_name": "git",
        "short_name": "g", 
        "description": "Git version control tasks",
        "global_tasks": []  # All tasks are namespaced
    },
    "development": {
        "module_name": "development",
        "short_name": "dev",
        "description": "Development and testing tasks", 
        "global_tasks": []  # All tasks are namespaced
    },
    "utils": {
        "module_name": "utils",
        "short_name": "u",
        "description": "Utility and helper tasks",
        "global_tasks": ["hello"]  # Only hello is global
    }
}
```

## Development

### Project Structure

```
samosa/
├── src/samosa/
│   ├── cli.py              # Main CLI entry point
│   └── tasks/
│       ├── __init__.py     # Task discovery and collections
│       ├── config.py       # Task configuration
│       ├── git.py          # Git operations
│       ├── development.py  # Dev tasks
│       └── utils.py        # Utility tasks
├── pyproject.toml          # Project configuration
├── LICENSE
└── README.md
```

### Adding New Tasks

1. Create a new task module in `src/samosa/tasks/`
2. Add task configuration to `config.py` (optional)
3. Tasks are auto-discovered and available immediately

```python
# Example: src/samosa/tasks/docker.py
from invoke import task

@task
def build_image(ctx, tag="latest"):
    """Build Docker image."""
    ctx.run(f"docker build -t myapp:{tag} .")

@task  
def run_container(ctx, port="8000"):
    """Run Docker container."""
    ctx.run(f"docker run -p {port}:8000 myapp")
```

## Best Practices

### Git Worktree Usage
- Use `samosa g worktree add <branch>` for clean feature development
- Worktrees are created in parent directory with format: `{project}-{branch}`
- Automatic branch fetching and tracking for existing remote branches

### Command Organization
- Global tasks: Available directly (`samosa hello`)
- Namespaced tasks: Available via namespace (`samosa dev lint`, `samosa g status`)
- Use short aliases for frequently used commands

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
