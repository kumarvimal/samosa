"""Development-focused tasks for code quality and testing."""

import subprocess
from pathlib import Path

from invoke import task


def get_git_root():
    """Get git repository root directory, or None if not in a git repo."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
        return Path(result.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def get_target_directory():
    """Get target directory - git root if in git repo, otherwise current directory."""
    git_root = get_git_root()
    if git_root:
        print(f"Using git repository root: {git_root}")
        return git_root
    else:
        current_dir = Path.cwd()
        print(f"Using current directory: {current_dir}")
        return current_dir


def get_python_paths(target_dir=None):
    """Get paths to check for Python code."""
    if target_dir is None:
        target_dir = get_target_directory()

    paths = []

    # Check for common Python directories
    potential_paths = ["src", ".", "tests", "test"]

    for path_name in potential_paths:
        path = target_dir / path_name
        if path.exists() and any(path.rglob("*.py")):
            # Use relative path from target directory
            if path_name == ".":
                paths.append(".")
            else:
                paths.append(path_name)

    if not paths:
        # Fallback to current directory if no Python files found in common locations
        paths = ["."]

    return " ".join(paths)


@task
def lint(ctx):
    """Run code linting with ruff."""
    print("Running ruff linter...")
    target_dir = get_target_directory()

    # Change to target directory for command execution
    with ctx.cd(target_dir):
        paths = get_python_paths(target_dir)
        print(f"Linting paths: {paths}")
        ctx.run(f"ruff check {paths}")


@task
def format(ctx):
    """Format code with black and ruff."""
    print("Formatting code...")
    target_dir = get_target_directory()

    # Change to target directory for command execution
    with ctx.cd(target_dir):
        paths = get_python_paths(target_dir)
        print(f"Formatting paths: {paths}")
        ctx.run(f"black {paths}")
        ctx.run(f"ruff format {paths}")


@task
def typecheck(ctx):
    """Run type checking with mypy."""
    print("Running type checker...")
    target_dir = get_target_directory()

    # Change to target directory for command execution
    with ctx.cd(target_dir):
        # For mypy, be smart about path selection to avoid duplicate modules
        paths = []
        
        # Check if there's a src directory (structured project)
        if (target_dir / "src").exists() and any((target_dir / "src").rglob("*.py")):
            paths.append("src")
            # Add test directories if they exist
            if (target_dir / "tests").exists() and any((target_dir / "tests").rglob("*.py")):
                paths.append("tests")
            elif (target_dir / "test").exists() and any((target_dir / "test").rglob("*.py")):
                paths.append("test")
        else:
            # No src directory, use root directory which includes everything
            paths.append(".")
        
        paths_str = " ".join(paths)
        print(f"Type checking paths: {paths_str}")
        ctx.run(f"mypy {paths_str}")


@task
def test(ctx, coverage=True):
    """Run tests with pytest.

    Args:
        coverage: Run with coverage report (default: True)
    """
    print("Running tests...")
    target_dir = get_target_directory()

    # Change to target directory for command execution
    with ctx.cd(target_dir):
        # Check for test directories in target directory
        test_dirs = []
        for test_dir in ["tests", "test"]:
            if (target_dir / test_dir).exists():
                test_dirs.append(test_dir)

        if not test_dirs:
            print("No tests directory found. Skipping tests.")
            return

        cmd = "pytest"
        if not coverage:
            cmd += " --no-cov"

        # Add test directories to command
        cmd += f" {' '.join(test_dirs)}"
        print(f"Running tests: {cmd}")
        ctx.run(cmd)


@task(pre=[lint, typecheck])
def check(ctx):
    """Run all code quality checks."""
    print("All development checks completed!")
