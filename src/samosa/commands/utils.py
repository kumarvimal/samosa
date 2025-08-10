"""Utility and helper commands."""

import os
from pathlib import Path
import shutil
import subprocess

import click
from invoke import Context


def get_project_config():
    """Read project configuration from package metadata or pyproject.toml."""
    config = {
        "name": "samosa",
        "version": "unknown",
        "description": "A Python CLI tool for task automation and project management",
    }

    try:
        # First try to get info from installed package metadata
        try:
            from importlib.metadata import metadata, version
        except ImportError:
            # Python < 3.8 fallback
            from importlib_metadata import metadata, version
        meta = metadata("samosa")
        config.update(
            {
                "name": meta.get("Name", "samosa"),
                "version": version("samosa"),
                "description": meta.get("Summary", config["description"]),
            }
        )
        return config
    except Exception:
        pass

    try:
        # Fallback: read from pyproject.toml (for development)
        import tomllib

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
                config.update(
                    {
                        "name": project_config.get("name", config["name"]),
                        "version": project_config.get("version", config["version"]),
                        "description": project_config.get(
                            "description", config["description"]
                        ),
                    }
                )
    except Exception:
        pass

    return config


@click.group()
def utils():
    """Utility and helper commands."""


@utils.command()
def info():
    """Show project information."""
    config = get_project_config()
    click.echo(f"{config['name'].title()} CLI Tool")
    click.echo(f"Version: {config['version']}")
    click.echo(config["description"])


@utils.command()
def env():
    """Show environment information."""
    import platform
    import sys

    ctx = Context()

    click.echo(f"Python version: {sys.version}")
    click.echo(f"Platform: {platform.platform()}")
    click.echo(f"Working directory: {ctx.cwd}")


@utils.command("install-alias")
@click.option(
    "--shell",
    default="auto",
    type=click.Choice(["auto", "bash", "zsh", "fish"]),
    help="Shell to configure (auto, bash, zsh, fish). Default: auto-detect",
)
def install_alias(shell):
    """Install shell alias 's' for samosa command."""
    ctx = Context()

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
            click.echo(
                "⚠️  Could not auto-detect shell. Please specify: --shell bash|zsh|fish",
                err=True,
            )
            return

    # Check if samosa is available
    samosa_path = shutil.which("samosa")
    if not samosa_path:
        click.echo("❌ samosa command not found in PATH", err=True)
        click.echo("💡 Make sure samosa is installed globally first")
        return

    click.echo(f"🔍 Found samosa at: {samosa_path}")
    click.echo(f"🐚 Configuring {shell} shell...")

    # Check if 's' command/alias already exists in current session
    try:
        s_command_check = ctx.run("command -v s", hide=True, warn=True)
        if s_command_check.ok:
            s_path = s_command_check.stdout.strip()
            click.echo(f"⚠️  Warning: 's' command already exists: {s_path}")

            # Check if it's already pointing to samosa
            if "samosa" in s_path or s_path == samosa_path:
                click.echo("✅ 's' already points to samosa!")
                return
            else:
                if not click.confirm("❓ 's' exists but points elsewhere. Override?"):
                    click.echo("❌ Installation cancelled to avoid conflicts")
                    click.echo(f"💡 The existing 's' command points to: {s_path}")
                    return
                click.echo("🔄 Proceeding with override...")
    except Exception:
        # If command -v fails, assume 's' doesn't exist (which is fine)
        pass

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
            with open(config_path) as f:
                content = f.read()
                if "alias s=" in content or "alias s " in content:
                    alias_exists = True

        if alias_exists:
            click.echo(f"✅ Alias 's' already exists in {config_path}")
            success = True
            continue

        try:
            # Add alias to config file
            with open(config_path, "a") as f:
                f.write(f"\n# Samosa CLI alias\n{alias_line}\n")

            click.echo(f"✅ Added alias to {config_path}")
            success = True

        except Exception as e:
            click.echo(f"❌ Failed to write to {config_path}: {e}", err=True)
            continue

    if success:
        click.echo("\n🎉 Shell alias installed successfully!")
        click.echo(f"📝 Added: {alias_line}")
        click.echo("\n🔄 To use the alias, either:")
        click.echo("   • Restart your terminal, or")
        if shell == "zsh":
            click.echo("   • Run: source ~/.zshrc")
        elif shell == "bash":
            click.echo("   • Run: source ~/.bashrc")
        elif shell == "fish":
            click.echo("   • Run: source ~/.config/fish/config.fish")

        click.echo("\n✨ Now you can use:")
        click.echo("   s git status    # instead of samosa git status")
        click.echo("   s utils info    # instead of samosa utils info")
        click.echo("   s --help        # instead of samosa --help")

    else:
        click.echo("❌ Failed to install alias to any config file", err=True)
        click.echo("💡 You can manually add this line to your shell config:")
        click.echo(f"   {alias_line}")


@utils.command("uninstall-alias")
@click.option(
    "--shell",
    default="auto",
    type=click.Choice(["auto", "bash", "zsh", "fish"]),
    help="Shell to configure (auto, bash, zsh, fish). Default: auto-detect",
)
def uninstall_alias(shell):
    """Remove shell alias 's' for samosa command."""
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
            click.echo(
                "⚠️  Could not auto-detect shell. Please specify: --shell bash|zsh|fish",
                err=True,
            )
            return

    click.echo(f"🐚 Removing samosa alias from {shell} shell...")

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
            with open(config_path) as f:
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
                click.echo(f"✅ Removed alias from {config_path}")
                success = True
            else:
                click.echo(f"i  No alias found in {config_path}")

        except Exception as e:
            click.echo(f"❌ Failed to modify {config_path}: {e}", err=True)

    if success:
        click.echo("\n🗑️  Shell alias removed!")
        click.echo(
            "🔄 Restart your terminal or source your shell config to apply changes"
        )
    else:
        click.echo("i  No samosa aliases found to remove")


@utils.command("install-completion")
@click.option(
    "--shell",
    default="auto",
    type=click.Choice(["auto", "bash", "zsh", "fish"]),
    help="Shell to configure (auto, bash, zsh, fish). Default: auto-detect",
)
def install_completion(shell):
    """Install shell completion for samosa command."""
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
            click.echo(
                "⚠️  Could not auto-detect shell. Please specify: --shell bash|zsh|fish",
                err=True,
            )
            return

    # Check if samosa is available
    samosa_path = shutil.which("samosa")
    if not samosa_path:
        click.echo("❌ samosa command not found in PATH", err=True)
        click.echo("💡 Make sure samosa is installed globally first")
        return

    click.echo(f"🔍 Found samosa at: {samosa_path}")
    click.echo(f"🐚 Installing {shell} completion...")

    try:
        if shell == "bash":
            # Generate bash completion script
            result = subprocess.run(
                [samosa_path, "--complete", "bash"],
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
                        click.echo(f"✅ Installed completion to {comp_path}")
                        break
                    else:
                        # For .bash_completion, append
                        completion_marker = "# Samosa completion"
                        if comp_path.exists():
                            with open(comp_path) as f:
                                if completion_marker in f.read():
                                    click.echo(
                                        f"✅ Completion already exists in {comp_path}"
                                    )
                                    break

                        with open(comp_path, "a") as f:
                            f.write(f"\n{completion_marker}\n{completion_script}\n")
                        click.echo(f"✅ Added completion to {comp_path}")
                        break
                except Exception as e:
                    click.echo(f"⚠️  Failed to write to {comp_path}: {e}")
                    continue

        elif shell == "zsh":
            # For zsh, Click provides built-in completion
            completion_script = """#compdef samosa
eval "$(_SAMOSA_COMPLETE=zsh_complete samosa)"
"""

            # Install to zsh completion directory
            zsh_comp_dir = Path("~/.zsh/completions").expanduser()
            zsh_comp_dir.mkdir(parents=True, exist_ok=True)

            comp_file = zsh_comp_dir / "_samosa"
            with open(comp_file, "w") as f:
                f.write(completion_script)
            click.echo(f"✅ Installed completion to {comp_file}")

            # Add to .zshrc if not already there
            zshrc_path = Path("~/.zshrc").expanduser()
            completion_setup = (
                "fpath=(~/.zsh/completions $fpath)\nautoload -U compinit && compinit"
            )

            if zshrc_path.exists():
                with open(zshrc_path) as f:
                    content = f.read()
                    if ".zsh/completions" not in content:
                        with open(zshrc_path, "a") as f:
                            f.write(
                                f"\n# Samosa completion setup\n{completion_setup}\n"
                            )
                        click.echo(f"✅ Added completion setup to {zshrc_path}")
                    else:
                        click.echo(f"✅ Completion setup already in {zshrc_path}")

        elif shell == "fish":
            # For fish, Click provides built-in completion
            completion_script = """eval (env _SAMOSA_COMPLETE=fish_complete samosa)
"""

            # Install to fish completion directory
            fish_comp_dir = Path("~/.config/fish/completions").expanduser()
            fish_comp_dir.mkdir(parents=True, exist_ok=True)

            comp_file = fish_comp_dir / "samosa.fish"
            with open(comp_file, "w") as f:
                f.write(completion_script)
            click.echo(f"✅ Installed completion to {comp_file}")

        click.echo("\n🎉 Shell completion installed successfully!")
        click.echo("\n🔄 To activate completion:")
        if shell == "bash":
            click.echo("   • Restart terminal or run: source ~/.bash_completion")
        elif shell == "zsh":
            click.echo("   • Restart terminal or run: exec zsh")
        elif shell == "fish":
            click.echo("   • Restart terminal or start new fish session")

        click.echo("\n✨ Now you can use TAB completion:")
        click.echo("   samosa <TAB>         # Show all commands")
        click.echo("   samosa git <TAB>     # Show git commands")
        click.echo("   samosa git backup <TAB> # Show backup commands")

    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Failed to generate completion script: {e}", err=True)
        click.echo("💡 Using Click's built-in completion system instead")
    except Exception as e:
        click.echo(f"❌ Error installing completion: {e}", err=True)


@utils.command("uninstall-completion")
@click.option(
    "--shell",
    default="auto",
    type=click.Choice(["auto", "bash", "zsh", "fish"]),
    help="Shell to configure (auto, bash, zsh, fish). Default: auto-detect",
)
def uninstall_completion(shell):
    """Remove shell completion for samosa command."""
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
            click.echo(
                "⚠️  Could not auto-detect shell. Please specify: --shell bash|zsh|fish",
                err=True,
            )
            return

    click.echo(f"🐚 Removing {shell} completion...")

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
                    click.echo(f"✅ Removed {comp_path}")
                    success = True
                else:
                    # Remove from .bash_completion file
                    try:
                        with open(comp_path) as f:
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
                            click.echo(f"✅ Removed completion from {comp_path}")
                            success = True
                    except Exception as e:
                        click.echo(f"⚠️  Failed to modify {comp_path}: {e}")

    elif shell == "zsh":
        # Remove zsh completion file
        comp_file = Path("~/.zsh/completions/_samosa").expanduser()
        if comp_file.exists():
            comp_file.unlink()
            click.echo(f"✅ Removed {comp_file}")
            success = True
        else:
            click.echo(f"i  No completion file found at {comp_file}")

    elif shell == "fish":
        # Remove fish completion file
        comp_file = Path("~/.config/fish/completions/samosa.fish").expanduser()
        if comp_file.exists():
            comp_file.unlink()
            click.echo(f"✅ Removed {comp_file}")
            success = True
        else:
            click.echo(f"i  No completion file found at {comp_file}")

    if success:
        click.echo("\n🗑️  Shell completion removed!")
        click.echo("🔄 Restart your terminal to apply changes")
    else:
        click.echo("i  No samosa completions found to remove")
