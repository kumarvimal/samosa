"""Utility and helper tasks."""

from invoke import task
import tomllib
from pathlib import Path


def get_project_config():
    """Read project configuration from package metadata or pyproject.toml."""
    config = {
        "name": "samosa",
        "version": "unknown",
        "description": "A Python CLI tool for task automation and project management"
    }
    
    try:
        # First try to get info from installed package metadata
        try:
            from importlib.metadata import metadata, version
        except ImportError:
            # Python < 3.8 fallback
            from importlib_metadata import metadata, version
        meta = metadata("samosa")
        config.update({
            "name": meta.get("Name", "samosa"),
            "version": version("samosa"),
            "description": meta.get("Summary", config["description"])
        })
        return config
    except Exception:
        pass
    
    try:
        # Fallback: read from pyproject.toml (for development)
        # Find pyproject.toml (go up from current file location to project root)
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent.parent
        pyproject_path = project_root / "pyproject.toml"
        
        if not pyproject_path.exists():
            # Fallback: try current working directory
            pyproject_path = Path.cwd() / "pyproject.toml"
            
        if pyproject_path.exists():
            with open(pyproject_path, "rb") as f:
                toml_config = tomllib.load(f)
                project_config = toml_config.get("project", {})
                config.update({
                    "name": project_config.get("name", config["name"]),
                    "version": project_config.get("version", config["version"]),
                    "description": project_config.get("description", config["description"])
                })
    except Exception:
        pass
    
    return config


@task
def hello(ctx, name="World"):
    """Say hello to someone.

    Args:
        name: Name to greet (default: World)
    """
    print(f"Hello, {name}!")


@task
def info(ctx):
    """Show project information."""
    config = get_project_config()
    print(f"{config['name'].title()} CLI Tool")
    print(f"Version: {config['version']}")
    print(config['description'])


@task
def env(ctx):
    """Show environment information."""
    import platform
    import sys

    print(f"Python version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Working directory: {ctx.cwd}")


@task
def install_alias(ctx, shell="auto"):
    """Install shell alias 's' for samosa command.

    Args:
        shell: Shell to configure (auto, bash, zsh, fish). Default: auto-detect
    """
    import os
    import shutil
    from pathlib import Path

    # Detect shell if auto
    if shell == "auto":
        shell_path = os.environ.get("SHELL", "").lower()
        if "zsh" in shell_path:
            shell = "zsh"
        elif "bash" in shell_path:
            shell = "bash"
        elif "fish" in shell_path:
            shell = "fish"
        else:
            print(
                "⚠️  Could not auto-detect shell. Please specify: --shell bash|zsh|fish"
            )
            return

    # Check if samosa is available
    samosa_path = shutil.which("samosa")
    if not samosa_path:
        print("❌ samosa command not found in PATH")
        print("💡 Make sure samosa is installed globally first")
        return

    print(f"🔍 Found samosa at: {samosa_path}")
    print(f"🐚 Configuring {shell} shell...")

    # Define alias
    alias_line = 'alias s="samosa"'

    # Shell-specific configuration
    config_files = {
        "bash": ["~/.bashrc", "~/.bash_profile"],
        "zsh": ["~/.zshrc"],
        "fish": ["~/.config/fish/config.fish"],
    }

    if shell == "fish":
        alias_line = "alias s samosa"

    success = False
    for config_file in config_files.get(shell, []):
        config_path = Path(config_file).expanduser()

        # Create config directory if needed (especially for fish)
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Check if alias already exists
        alias_exists = False
        if config_path.exists():
            with open(config_path, "r") as f:
                content = f.read()
                if "alias s=" in content or "alias s " in content:
                    alias_exists = True

        if alias_exists:
            print(f"✅ Alias 's' already exists in {config_path}")
            success = True
            continue

        try:
            # Add alias to config file
            with open(config_path, "a") as f:
                f.write(f"\n# Samosa CLI alias\n{alias_line}\n")

            print(f"✅ Added alias to {config_path}")
            success = True

        except Exception as e:
            print(f"❌ Failed to write to {config_path}: {e}")
            continue

    if success:
        print(f"\n🎉 Shell alias installed successfully!")
        print(f"📝 Added: {alias_line}")
        print(f"\n🔄 To use the alias, either:")
        print(f"   • Restart your terminal, or")
        if shell == "zsh":
            print(f"   • Run: source ~/.zshrc")
        elif shell == "bash":
            print(f"   • Run: source ~/.bashrc")
        elif shell == "fish":
            print(f"   • Run: source ~/.config/fish/config.fish")

        print(f"\n✨ Now you can use:")
        print(f"   s g status    # instead of samosa g status")
        print(f"   s lint        # instead of samosa lint")
        print(f"   s --help      # instead of samosa --help")

    else:
        print("❌ Failed to install alias to any config file")
        print(f"💡 You can manually add this line to your shell config:")
        print(f"   {alias_line}")


@task
def uninstall_alias(ctx, shell="auto"):
    """Remove shell alias 's' for samosa command.

    Args:
        shell: Shell to configure (auto, bash, zsh, fish). Default: auto-detect
    """
    import os
    from pathlib import Path

    # Detect shell if auto
    if shell == "auto":
        shell_path = os.environ.get("SHELL", "").lower()
        if "zsh" in shell_path:
            shell = "zsh"
        elif "bash" in shell_path:
            shell = "bash"
        elif "fish" in shell_path:
            shell = "fish"
        else:
            print(
                "⚠️  Could not auto-detect shell. Please specify: --shell bash|zsh|fish"
            )
            return

    print(f"🐚 Removing samosa alias from {shell} shell...")

    # Shell-specific configuration files
    config_files = {
        "bash": ["~/.bashrc", "~/.bash_profile"],
        "zsh": ["~/.zshrc"],
        "fish": ["~/.config/fish/config.fish"],
    }

    success = False
    for config_file in config_files.get(shell, []):
        config_path = Path(config_file).expanduser()

        if not config_path.exists():
            continue

        try:
            # Read current content
            with open(config_path, "r") as f:
                lines = f.readlines()

            # Filter out samosa alias lines
            new_lines = []
            skip_next = False

            for line in lines:
                if skip_next:
                    skip_next = False
                    continue

                # Skip samosa alias comment
                if line.strip() == "# Samosa CLI alias":
                    skip_next = True  # Skip the next line (the actual alias)
                    continue

                # Skip direct alias lines
                if ("alias s=" in line and "samosa" in line) or (
                    "alias s " in line and "samosa" in line
                ):
                    continue

                new_lines.append(line)

            # Write back if changed
            if len(new_lines) != len(lines):
                with open(config_path, "w") as f:
                    f.writelines(new_lines)
                print(f"✅ Removed alias from {config_path}")
                success = True
            else:
                print(f"ℹ️  No alias found in {config_path}")

        except Exception as e:
            print(f"❌ Failed to modify {config_path}: {e}")

    if success:
        print(f"\n🗑️  Shell alias removed!")
        print(f"🔄 Restart your terminal or source your shell config to apply changes")
    else:
        print("ℹ️  No samosa aliases found to remove")


@task
def install_completion(ctx, shell="auto"):
    """Install shell completion for samosa command.

    Args:
        shell: Shell to configure (auto, bash, zsh, fish). Default: auto-detect
    """
    import os
    import shutil
    import subprocess
    from pathlib import Path

    # Detect shell if auto
    if shell == "auto":
        shell_path = os.environ.get("SHELL", "").lower()
        if "zsh" in shell_path:
            shell = "zsh"
        elif "bash" in shell_path:
            shell = "bash"
        elif "fish" in shell_path:
            shell = "fish"
        else:
            print(
                "⚠️  Could not auto-detect shell. Please specify: --shell bash|zsh|fish"
            )
            return

    # Check if samosa is available
    samosa_path = shutil.which("samosa")
    if not samosa_path:
        print("❌ samosa command not found in PATH")
        print("💡 Make sure samosa is installed globally first")
        return

    print(f"🔍 Found samosa at: {samosa_path}")
    print(f"🐚 Installing {shell} completion...")

    try:
        if shell == "bash":
            # Generate bash completion script
            result = subprocess.run(
                [samosa_path, "completion-script", "bash"],
                capture_output=True,
                text=True,
                check=True,
            )
            completion_script = result.stdout

            # Install to bash completion directory
            completion_paths = [
                Path("~/.bash_completion").expanduser(),
                Path("~/.local/share/bash-completion/completions/samosa").expanduser(),
            ]

            for comp_path in completion_paths:
                try:
                    comp_path.parent.mkdir(parents=True, exist_ok=True)

                    # For the completions directory, write to samosa file
                    if "completions" in str(comp_path):
                        with open(comp_path, "w") as f:
                            f.write(completion_script)
                        print(f"✅ Installed completion to {comp_path}")
                        break
                    else:
                        # For .bash_completion, append
                        completion_marker = "# Samosa completion"
                        if comp_path.exists():
                            with open(comp_path, "r") as f:
                                if completion_marker in f.read():
                                    print(
                                        f"✅ Completion already exists in {comp_path}"
                                    )
                                    break

                        with open(comp_path, "a") as f:
                            f.write(f"\n{completion_marker}\n{completion_script}\n")
                        print(f"✅ Added completion to {comp_path}")
                        break
                except Exception as e:
                    print(f"⚠️  Failed to write to {comp_path}: {e}")
                    continue

        elif shell == "zsh":
            # Generate zsh completion script
            result = subprocess.run(
                [samosa_path, "completion-script", "zsh"],
                capture_output=True,
                text=True,
                check=True,
            )
            completion_script = result.stdout

            # Install to zsh completion directory
            zsh_comp_dir = Path("~/.zsh/completions").expanduser()
            zsh_comp_dir.mkdir(parents=True, exist_ok=True)

            comp_file = zsh_comp_dir / "_samosa"
            with open(comp_file, "w") as f:
                f.write(completion_script)
            print(f"✅ Installed completion to {comp_file}")

            # Add to .zshrc if not already there
            zshrc_path = Path("~/.zshrc").expanduser()
            completion_setup = (
                f"fpath=(~/.zsh/completions $fpath)\nautoload -U compinit && compinit"
            )

            if zshrc_path.exists():
                with open(zshrc_path, "r") as f:
                    content = f.read()
                    if ".zsh/completions" not in content:
                        with open(zshrc_path, "a") as f:
                            f.write(
                                f"\n# Samosa completion setup\n{completion_setup}\n"
                            )
                        print(f"✅ Added completion setup to {zshrc_path}")
                    else:
                        print(f"✅ Completion setup already in {zshrc_path}")

        elif shell == "fish":
            # Generate fish completion script
            result = subprocess.run(
                [samosa_path, "completion-script", "fish"],
                capture_output=True,
                text=True,
                check=True,
            )
            completion_script = result.stdout

            # Install to fish completion directory
            fish_comp_dir = Path("~/.config/fish/completions").expanduser()
            fish_comp_dir.mkdir(parents=True, exist_ok=True)

            comp_file = fish_comp_dir / "samosa.fish"
            with open(comp_file, "w") as f:
                f.write(completion_script)
            print(f"✅ Installed completion to {comp_file}")

        print(f"\n🎉 Shell completion installed successfully!")
        print(f"\n🔄 To activate completion:")
        if shell == "bash":
            print(f"   • Restart terminal or run: source ~/.bash_completion")
        elif shell == "zsh":
            print(f"   • Restart terminal or run: exec zsh")
        elif shell == "fish":
            print(f"   • Restart terminal or start new fish session")

        print(f"\n✨ Now you can use TAB completion:")
        print(f"   samosa <TAB>     # Show all commands")
        print(f"   samosa g <TAB>   # Show git commands")
        print(f"   samosa git w<TAB> # Complete 'worktree'")

    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to generate completion script: {e}")
        print(
            "💡 Make sure you're using Click framework version that supports --completion"
        )
    except Exception as e:
        print(f"❌ Error installing completion: {e}")


@task
def uninstall_completion(ctx, shell="auto"):
    """Remove shell completion for samosa command.

    Args:
        shell: Shell to configure (auto, bash, zsh, fish). Default: auto-detect
    """
    import os
    from pathlib import Path

    # Detect shell if auto
    if shell == "auto":
        shell_path = os.environ.get("SHELL", "").lower()
        if "zsh" in shell_path:
            shell = "zsh"
        elif "bash" in shell_path:
            shell = "bash"
        elif "fish" in shell_path:
            shell = "fish"
        else:
            print(
                "⚠️  Could not auto-detect shell. Please specify: --shell bash|zsh|fish"
            )
            return

    print(f"🐚 Removing {shell} completion...")

    success = False

    if shell == "bash":
        # Remove from various bash completion locations
        completion_paths = [
            Path("~/.bash_completion").expanduser(),
            Path("~/.local/share/bash-completion/completions/samosa").expanduser(),
        ]

        for comp_path in completion_paths:
            if comp_path.exists():
                if "completions" in str(comp_path):
                    # Remove the entire file
                    comp_path.unlink()
                    print(f"✅ Removed {comp_path}")
                    success = True
                else:
                    # Remove from .bash_completion file
                    try:
                        with open(comp_path, "r") as f:
                            lines = f.readlines()

                        new_lines = []
                        skip_section = False

                        for line in lines:
                            if "# Samosa completion" in line:
                                skip_section = True
                                continue
                            elif skip_section and line.strip() == "":
                                skip_section = False
                                continue
                            elif not skip_section:
                                new_lines.append(line)

                        if len(new_lines) != len(lines):
                            with open(comp_path, "w") as f:
                                f.writelines(new_lines)
                            print(f"✅ Removed completion from {comp_path}")
                            success = True
                    except Exception as e:
                        print(f"⚠️  Failed to modify {comp_path}: {e}")

    elif shell == "zsh":
        # Remove zsh completion file
        comp_file = Path("~/.zsh/completions/_samosa").expanduser()
        if comp_file.exists():
            comp_file.unlink()
            print(f"✅ Removed {comp_file}")
            success = True
        else:
            print(f"ℹ️  No completion file found at {comp_file}")

    elif shell == "fish":
        # Remove fish completion file
        comp_file = Path("~/.config/fish/completions/samosa.fish").expanduser()
        if comp_file.exists():
            comp_file.unlink()
            print(f"✅ Removed {comp_file}")
            success = True
        else:
            print(f"ℹ️  No completion file found at {comp_file}")

    if success:
        print(f"\n🗑️  Shell completion removed!")
        print(f"🔄 Restart your terminal to apply changes")
    else:
        print("ℹ️  No samosa completions found to remove")
