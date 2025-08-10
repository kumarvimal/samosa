# Samosa Test Suite

This directory contains comprehensive tests for the samosa CLI tool, with special focus on the plugin system and utils module.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py                      # Pytest fixtures and configuration
├── test_cli.py                      # Main CLI interface tests
├── test_commands_integration.py     # Integration tests for all command groups
├── test_plugins.py                  # Plugin system tests (comprehensive)
├── test_utils.py                   # AliasedGroup utility tests (comprehensive)
└── README.md                       # This file
```

## Running Tests

### Quick Commands

```bash
# Run all tests with coverage (configured in pyproject.toml)
pytest

# Run all tests without coverage (faster for development)
pytest --no-cov

# Run with verbose output
pytest -v

# Run specific test files
pytest tests/test_plugins.py -v     # Plugin system tests
pytest tests/test_utils.py -v       # AliasedGroup utility tests
pytest tests/test_cli.py -v         # CLI interface tests

# Run by test markers
pytest -m unit -v                   # Unit tests only
pytest -m integration -v            # Integration tests only
pytest -m slow -v                   # Slow tests only
```

### Detailed pytest Usage

```bash
# Specific test class
pytest tests/test_plugins.py::TestProjectContext -v

# Specific test method
pytest tests/test_plugins.py::TestProjectContext::test_config_loading -v

# Stop at first failure
pytest -x

# Show coverage report in terminal
pytest --cov-report=term-missing

# Generate HTML coverage report
pytest --cov-report=html
```

## Test Coverage

### Plugin System Tests (`test_plugins.py`)

**ProjectContext class:**
- ✅ Initialization with project paths
- ✅ Configuration loading from YAML files
- ✅ Configuration caching behavior
- ✅ Handling missing/invalid config files
- ✅ Invoke context creation and delegation
- ✅ Shell command execution via `run()` method

**ProjectCommandLoader class:**
- ✅ Project root discovery (walking up directory tree)
- ✅ Handling multiple directory levels
- ✅ Behavior when no .samosa directory found
- ✅ Project discovery and initialization
- ✅ Dynamic command loading from Python files
- ✅ Ignoring invalid Python files gracefully
- ✅ Ignoring special files (__init__.py, __pycache__)
- ✅ Project context injection into loaded modules
- ✅ Local command group creation (with/without project)
- ✅ `samosa local init` command functionality

### Utils Module Tests (`test_utils.py`)

**AliasedGroup class:**
- ✅ Adding commands with multiple aliases
- ✅ Alias resolution in `get_command()`
- ✅ Command listing (excludes aliases to avoid duplicates)
- ✅ Help formatting showing "command (alias1, alias2)" format
- ✅ Command execution via aliases
- ✅ Handling commands with no aliases
- ✅ Handling commands with single alias
- ✅ Proper help output formatting

### CLI Tests (`test_cli.py`)

- ✅ Main CLI help output
- ✅ Version command functionality
- ✅ Hello command (with and without --name)
- ✅ Command aliases work (g, u, l)
- ✅ Invalid command handling

### Integration Tests (`test_commands_integration.py`)

**Git Commands:**
- ✅ Help output for git, backup, and worktree subcommands
- ✅ Mocked command execution (git status, git add)

**Dev Commands:**
- ✅ Help output for development commands
- ✅ Mocked command execution (lint, format)

**Utils Commands:**
- ✅ Help output and basic command functionality
- ✅ Info and env command outputs

**Local Commands:**
- ✅ Local group behavior with/without projects
- ✅ `samosa local init` creates proper structure
- ✅ Project-specific command discovery and execution
- ✅ Nested command execution (deploy app staging)

## Key Test Features

### Robust Fixtures

- **temp_project_dir**: Creates isolated temporary directories
- **samosa_project_dir**: Pre-configured with .samosa structure
- **sample_command_file**: Creates realistic project commands
- **mock_cwd**: Properly mocks current working directory

### Comprehensive Mocking

- Mocks invoke Context for shell command testing
- Handles path resolution across different OS temporary directories
- Safely tests file creation/deletion operations

### Edge Case Coverage

- Invalid YAML configuration files
- Missing directories and files  
- Invalid Python command files
- Path resolution with symlinks (/private/var vs /var)
- Empty and malformed project structures

### Integration Testing

- Tests entire command workflows end-to-end
- Verifies CLI argument parsing and help output
- Tests plugin system integration with main CLI
- Validates project discovery and command loading

## Test Quality Features

- **58 total tests** covering all major functionality
- **Path-safe**: Works across different OS and temp directory setups
- **Isolated**: Each test runs in its own temporary environment
- **Fast**: Core tests run in <0.1 seconds
- **Comprehensive**: Tests both happy path and error conditions
- **Realistic**: Uses actual project structures and command patterns

## Running Specific Test Scenarios

```bash
# Test plugin system comprehensively
pytest tests/test_plugins.py -v

# Test AliasedGroup functionality
pytest tests/test_utils.py -v

# Test CLI integration
pytest tests/test_cli.py -v

# Test command integration with mocking
pytest tests/test_commands_integration.py -v

# Test slow operations (marked with @pytest.mark.slow)
pytest -m slow -v

# Test integration scenarios (marked with @pytest.mark.integration)
pytest -m integration -v

# Test without coverage for speed
pytest --no-cov
```

This test suite provides confidence that both the plugin system and the AliasedGroup utility work correctly across a variety of real-world scenarios.