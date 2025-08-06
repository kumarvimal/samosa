"""Utility and helper tasks."""

from invoke import task


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
    print("Samosa CLI Tool")
    print("Version: 0.1.0")
    print("A Python CLI tool with invoke integration")


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
        shell_path = os.environ.get('SHELL', '').lower()
        if 'zsh' in shell_path:
            shell = 'zsh'
        elif 'bash' in shell_path:
            shell = 'bash'
        elif 'fish' in shell_path:
            shell = 'fish'
        else:
            print("⚠️  Could not auto-detect shell. Please specify: --shell bash|zsh|fish")
            return
    
    # Check if samosa is available
    samosa_path = shutil.which('samosa')
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
        'bash': ['~/.bashrc', '~/.bash_profile'],
        'zsh': ['~/.zshrc'],
        'fish': ['~/.config/fish/config.fish']
    }
    
    if shell == 'fish':
        alias_line = 'alias s samosa'
    
    success = False
    for config_file in config_files.get(shell, []):
        config_path = Path(config_file).expanduser()
        
        # Create config directory if needed (especially for fish)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if alias already exists
        alias_exists = False
        if config_path.exists():
            with open(config_path, 'r') as f:
                content = f.read()
                if 'alias s=' in content or 'alias s ' in content:
                    alias_exists = True
        
        if alias_exists:
            print(f"✅ Alias 's' already exists in {config_path}")
            success = True
            continue
            
        try:
            # Add alias to config file
            with open(config_path, 'a') as f:
                f.write(f'\n# Samosa CLI alias\n{alias_line}\n')
            
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
        if shell == 'zsh':
            print(f"   • Run: source ~/.zshrc")
        elif shell == 'bash':
            print(f"   • Run: source ~/.bashrc")
        elif shell == 'fish':
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
        shell_path = os.environ.get('SHELL', '').lower()
        if 'zsh' in shell_path:
            shell = 'zsh'
        elif 'bash' in shell_path:
            shell = 'bash'
        elif 'fish' in shell_path:
            shell = 'fish'
        else:
            print("⚠️  Could not auto-detect shell. Please specify: --shell bash|zsh|fish")
            return
    
    print(f"🐚 Removing samosa alias from {shell} shell...")
    
    # Shell-specific configuration files
    config_files = {
        'bash': ['~/.bashrc', '~/.bash_profile'],
        'zsh': ['~/.zshrc'], 
        'fish': ['~/.config/fish/config.fish']
    }
    
    success = False
    for config_file in config_files.get(shell, []):
        config_path = Path(config_file).expanduser()
        
        if not config_path.exists():
            continue
            
        try:
            # Read current content
            with open(config_path, 'r') as f:
                lines = f.readlines()
            
            # Filter out samosa alias lines
            new_lines = []
            skip_next = False
            
            for line in lines:
                if skip_next:
                    skip_next = False
                    continue
                    
                # Skip samosa alias comment
                if line.strip() == '# Samosa CLI alias':
                    skip_next = True  # Skip the next line (the actual alias)
                    continue
                    
                # Skip direct alias lines
                if ('alias s=' in line and 'samosa' in line) or ('alias s ' in line and 'samosa' in line):
                    continue
                    
                new_lines.append(line)
            
            # Write back if changed
            if len(new_lines) != len(lines):
                with open(config_path, 'w') as f:
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
