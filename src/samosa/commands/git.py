"""Git-related commands. There are better tools available, it's all about personalization"""
from datetime import datetime
from pathlib import Path

import click
from invoke import Context

# Import the AliasedGroup from utils module
from ..utils import AliasedGroup


@click.group(cls=AliasedGroup)
def git():
    """Git version control commands."""
    pass


@git.command()
def status():
    """Show git status."""
    ctx = Context()
    ctx.run("git status")


@git.command()
@click.option("--files", default=".", help="Files to add (default: all files)")
def add(files):
    """Add files to git staging."""
    ctx = Context()
    ctx.run(f"git add {files}")


@git.command()
@click.argument("message")
def commit(message):
    """Create a git commit."""
    ctx = Context()
    ctx.run(f'git commit -m "{message}"')


@git.command()
@click.option("--remote", default="origin", help="Remote name (default: origin)")
@click.option("--branch", help="Branch to push (default: current branch)")
def push(remote, branch):
    """Push changes to remote."""
    ctx = Context()
    if branch:
        ctx.run(f"git push {remote} {branch}")
    else:
        ctx.run(f"git push {remote}")


@git.command()
@click.option("--remote", default="origin", help="Remote name (default: origin)")  
@click.option("--branch", help="Branch to pull (default: current branch)")
def pull(remote, branch):
    """Pull changes from remote."""
    ctx = Context()
    if branch:
        ctx.run(f"git pull {remote} {branch}")
    else:
        ctx.run(f"git pull {remote}")


@git.command()
@click.argument("branch")
def merge(branch):
    """Merge a branch into current branch."""
    ctx = Context()
    ctx.run(f"git merge {branch}")


@git.command()
@click.argument("branch")
@click.option("--create", is_flag=True, help="Create new branch if it doesn't exist")
def checkout(branch, create):
    """Checkout a branch."""
    ctx = Context()
    if create:
        ctx.run(f"git checkout -b {branch}")
    else:
        ctx.run(f"git checkout {branch}")


@git.command()
@click.option("--remote", default="origin", help="Remote name (default: origin)")
@click.option("--main-branch", help="Main branch name (auto-detected if not provided)")
def sync(remote, main_branch):
    """Sync current branch with remote main."""
    ctx = Context()
    
    try:
        # Get current branch name
        result = ctx.run("git branch --show-current", hide=True)
        current_branch = result.stdout.strip()
        
        if not current_branch:
            click.echo("❌ Could not determine current branch", err=True)
            return
        
        # Auto-detect main branch if not provided
        if not main_branch or main_branch.strip() == "":
            try:
                # Try to get the default branch from remote HEAD
                result = ctx.run(f"git symbolic-ref refs/remotes/{remote}/HEAD", hide=True, warn=True)
                if result.ok:
                    main_branch = result.stdout.strip().split('/')[-1]
                else:
                    # Fallback: try common main branch names
                    for branch in ['main', 'master', 'develop']:
                        result = ctx.run(f"git ls-remote --heads {remote} {branch}", hide=True, warn=True)
                        if result.ok and result.stdout.strip():
                            main_branch = branch
                            break
                    
                    if not main_branch:
                        main_branch = "main"
                        
            except Exception:
                main_branch = "main"
        
        click.echo(f"🔄 Syncing branch '{current_branch}' with {remote}/{main_branch}...")
        
        click.echo("📥 Fetching latest changes...")
        ctx.run(f"git fetch {remote}")
        
        click.echo(f"🔀 Rebasing {current_branch} onto {remote}/{main_branch}...")
        ctx.run(f"git rebase {remote}/{main_branch}")
        
        click.echo("✅ Branch synced successfully!")
        
    except Exception as e:
        click.echo(f"❌ Error syncing branch: {e}", err=True)
        click.echo("💡 Make sure you have no uncommitted changes and the remote exists", err=True)
        raise click.ClickException("Failed to sync branch")


@git.command()
def browse():
    """Open current git repository in GitHub in the browser."""
    import re
    import webbrowser
    
    ctx = Context()

    try:
        # Get the remote URL
        result = ctx.run("git remote get-url origin", hide=True)
        remote_url = result.stdout.strip()

        if not remote_url:
            click.echo("❌ No remote 'origin' found", err=True)
            return

        click.echo(f"🔍 Found remote URL: {remote_url}")

        # Convert various Git URL formats to GitHub web URL
        github_url = None

        # Handle SSH format: git@github.com:user/repo.git
        ssh_match = re.match(r"git@github\.com:([^/]+)/(.+)\.git$", remote_url)
        if ssh_match:
            user, repo = ssh_match.groups()
            github_url = f"https://github.com/{user}/{repo}"

        # Handle HTTPS format: https://github.com/user/repo.git
        elif re.match(r"https://github\.com/([^/]+)/(.+?)\.git$", remote_url):
            https_match = re.match(
                r"https://github\.com/([^/]+)/(.+?)\.git$", remote_url
            )
            user, repo = https_match.groups()
            github_url = f"https://github.com/{user}/{repo}"

        # Handle HTTPS without .git: https://github.com/user/repo
        elif re.match(r"https://github\.com/([^/]+)/([^/]+)/?$", remote_url):
            https_no_git_match = re.match(
                r"https://github\.com/([^/]+)/([^/]+)/?$", remote_url
            )
            user, repo = https_no_git_match.groups()
            github_url = f"https://github.com/{user}/{repo}"

        if github_url:
            click.echo(f"🌐 Opening: {github_url}")
            webbrowser.open(github_url)
            click.echo("✅ Repository opened in browser!")
        else:
            click.echo(f"❌ Could not parse GitHub URL from: {remote_url}", err=True)
            click.echo(
                "💡 Supported formats: git@github.com:user/repo.git or https://github.com/user/repo.git",
                err=True
            )

    except Exception as e:
        click.echo(f"❌ Error opening repository: {e}", err=True)
        click.echo("💡 Make sure you're in a git repository with a GitHub remote", err=True)
        raise click.ClickException("Failed to open repository")


# Backup subcommand group
@click.group()
def backup():
    """Backup branch management commands."""
    pass

# Add backup command with alias
git.add_command_with_aliases(backup, name="backup", aliases=["b"])


@backup.command("add")
def backup_add():
    """Create a backup branch from the current branch."""
    ctx = Context()
    
    try:
        # Get current branch name
        result = ctx.run("git branch --show-current", hide=True)
        current_branch = result.stdout.strip()
        
        if not current_branch:
            click.echo("❌ Could not determine current branch", err=True)
            return
        
        now = datetime.now()
        timestamp = now.strftime("%H-%M-%S_%d-%m-%Y")
        backup_branch = f"backup/{current_branch}-{timestamp}"

        if click.confirm("❓ Create backup branch?"):
            click.echo(f"💾 Creating backup branch: {backup_branch}")
            ctx.run(f"git branch {backup_branch}")
            click.echo(f"✅ Backup branch '{backup_branch}' created successfully!")
        else:
            click.echo("❌ Backup creation cancelled")
        
    except Exception as e:
        click.echo(f"❌ Error creating backup branch: {e}", err=True)
        click.echo("💡 Make sure you're in a git repository and have commits", err=True)
        raise click.ClickException("Failed to create backup")


@backup.command("list")
def backup_list():
    """List all backup branches for the current branch."""
    ctx = Context()
    
    try:
        # Get current branch name
        result = ctx.run("git branch --show-current", hide=True)
        current_branch = result.stdout.strip()
        
        if not current_branch:
            click.echo("❌ Could not determine current branch", err=True)
            return
        
        click.echo(f"🔍 Backup branches for '{current_branch}':")
        
        # Get all branches and filter for backups of current branch
        result = ctx.run("git branch -a", hide=True)
        branches = result.stdout.strip().split('\n')
        
        backup_pattern = f"backup/{current_branch}-"
        backups = []
        
        for branch in branches:
            # Clean up branch name (remove * and whitespace)
            clean_branch = branch.strip().lstrip('* ').replace('remotes/origin/', '')
            if backup_pattern in clean_branch:
                backups.append(clean_branch)
        
        if backups:
            for backup in sorted(backups):
                click.echo(f"  📦 {backup}")
            click.echo(f"\n✅ Found {len(backups)} backup(s)")
        else:
            click.echo(f"  💭 No backup branches found for '{current_branch}'")
            
    except Exception as e:
        click.echo(f"❌ Error listing backup branches: {e}", err=True)
        click.echo("💡 Make sure you're in a git repository", err=True)
        raise click.ClickException("Failed to list backups")


@backup.command("delete")
@click.option("--all", "delete_all", is_flag=True, help="Delete all backup branches for current branch")
@click.option("--branch", help="Delete specific backup branch by name (without backup/ prefix)")
def backup_delete(delete_all, branch):
    """Delete backup branches for the current branch."""
    ctx = Context()
    
    try:
        # Get current branch name
        result = ctx.run("git branch --show-current", hide=True)
        current_branch = result.stdout.strip()
        
        if not current_branch:
            click.echo("❌ Could not determine current branch", err=True)
            return
        
        if branch:
            # Delete specific backup branch
            # Failsafe: ensure we only delete backup branches
            if not branch.startswith("backup/"):
                # If user provided branch without backup/ prefix, add it
                if "/" not in branch:
                    backup_branch = f"backup/{branch}"
                else:
                    # If user provided full branch name, ensure it starts with backup/
                    if not branch.startswith("backup/"):
                        click.echo(f"❌ Safety check failed: Can only delete backup branches (must start with 'backup/')", err=True)
                        click.echo(f"💡 You provided: '{branch}' - this doesn't look like a backup branch", err=True)
                        click.echo("💡 Use 'samosa git backup list' to see available backup branches", err=True)
                        return
                    backup_branch = branch
            else:
                backup_branch = branch
            
            # Check if branch exists
            result = ctx.run("git branch", hide=True)
            branches = result.stdout.strip().split('\n')
            
            branch_exists = False
            for b in branches:
                clean_branch = b.strip().lstrip('* ')
                if clean_branch == backup_branch:
                    branch_exists = True
                    break
            
            if not branch_exists:
                click.echo(f"❌ Backup branch '{backup_branch}' not found", err=True)
                click.echo("💡 Use 'samosa git backup list' to see available backups", err=True)
                return
            
            click.echo(f"🗑️  Deleting backup branch: {backup_branch}")
            
            # Ask for confirmation with red warning
            click.echo(f"\n\033[91m⚠️  WARNING: This will permanently delete backup branch '{backup_branch}'!\033[0m", err=True)
            if click.confirm(f"\033[91m❓ Are you sure you want to delete this backup branch?\033[0m"):
                try:
                    # Final safety check before deletion
                    if not backup_branch.startswith("backup/"):
                        click.echo(f"❌ SAFETY ABORT: Refusing to delete non-backup branch '{backup_branch}'", err=True)
                        return
                    
                    ctx.run(f"git branch -D {backup_branch}")
                    click.echo(f"✅ Successfully deleted backup branch '{backup_branch}'")
                except Exception as e:
                    click.echo(f"❌ Failed to delete {backup_branch}: {e}", err=True)
            else:
                click.echo("❌ Backup deletion cancelled")
                
        elif delete_all:
            # Delete all backup branches for current branch
            click.echo(f"🗑️  Deleting all backup branches for '{current_branch}'...")
            
            # Get all local branches and filter for backups of current branch
            result = ctx.run("git branch", hide=True)
            branches = result.stdout.strip().split('\n')
            
            backup_pattern = f"backup/{current_branch}-"
            local_backups = []
            
            for b in branches:
                # Clean up branch name (remove * and whitespace)
                clean_branch = b.strip().lstrip('* ')
                # Failsafe: double-check that this is actually a backup branch
                if backup_pattern in clean_branch and clean_branch.startswith("backup/"):
                    local_backups.append(clean_branch)
            
            if not local_backups:
                click.echo(f"  💭 No local backup branches found for '{current_branch}'")
                return
            
            click.echo(f"📋 Found {len(local_backups)} backup branch(es) to delete:")
            for backup in sorted(local_backups):
                click.echo(f"  📦 {backup}")
            
            # Ask for confirmation with red warning
            click.echo(f"\n\033[91m⚠️  WARNING: This will permanently delete {len(local_backups)} backup branch(es)!\033[0m", err=True)
            if click.confirm(f"\033[91m❓ Are you sure you want to delete all backup branches?\033[0m"):
                deleted_count = 0
                for backup in local_backups:
                    try:
                        # Final safety check before deletion
                        if not backup.startswith("backup/"):
                            click.echo(f"  ❌ SAFETY ABORT: Skipping non-backup branch '{backup}'", err=True)
                            continue
                        
                        ctx.run(f"git branch -D {backup}")
                        click.echo(f"  🗑️  Deleted: {backup}")
                        deleted_count += 1
                    except Exception as e:
                        click.echo(f"  ❌ Failed to delete {backup}: {e}", err=True)
                
                if deleted_count > 0:
                    click.echo(f"✅ Successfully deleted {deleted_count}/{len(local_backups)} backup branch(es)")
                else:
                    click.echo("❌ No backup branches were deleted")
            else:
                click.echo("❌ Backup deletion cancelled")
        else:
            # No options provided, show help
            click.echo("❌ Please specify either --all to delete all backups or --branch to delete a specific backup", err=True)
            click.echo("💡 Usage:", err=True)
            click.echo("   samosa git backup delete --all", err=True)
            click.echo("   samosa git backup delete --branch main-21-36-47_08-08-2025", err=True)
            click.echo("   samosa git backup list  # to see available backups", err=True)
            
    except Exception as e:
        click.echo(f"❌ Error deleting backup branches: {e}", err=True)
        click.echo("💡 Make sure you're in a git repository", err=True)
        raise click.ClickException("Failed to delete backups")


# Worktree subcommand group  
@click.group()
def worktree():
    """Git worktree management commands."""
    pass

# Add worktree command with alias
git.add_command_with_aliases(worktree, name="worktree", aliases=["w"])


@worktree.command("add")
@click.argument("branch")
@click.option("--base", default="", help="Base branch/commit to create new branch from (default: current branch)")
@click.option("--fetch/--no-fetch", default=True, help="Fetch latest remote changes before creating worktree (default: True)")
def worktree_add(branch, base, fetch):
    """Create a git worktree one directory up with project-name-branch format."""
    ctx = Context()
    
    current_dir = Path.cwd()
    project_name = current_dir.name

    # Convert branch name to directory-safe format
    # feat/some-feature -> feat-some-feature
    safe_branch = branch.replace("/", "-")

    # Create worktree directory name: project-name-branch
    worktree_name = f"{project_name}-{safe_branch}"

    # Path to create worktree (one directory up)
    worktree_path = current_dir.parent / worktree_name

    click.echo(f"Creating worktree for branch '{branch}' at: {worktree_path}")

    try:
        # Fetch latest changes if requested
        if fetch:
            click.echo("🔄 Fetching latest changes...")
            ctx.run("git fetch --all", warn=True)

        # Check if branch exists locally
        local_result = ctx.run("git branch --list", hide=True, warn=True)
        local_branches = local_result.stdout if local_result.ok else ""

        # Check if branch exists remotely
        remote_result = ctx.run("git branch -r", hide=True, warn=True)
        remote_branches = remote_result.stdout if remote_result.ok else ""

        branch_exists_locally = (
            f" {branch}\n" in local_branches or f"* {branch}\n" in local_branches
        )
        branch_exists_remotely = f"origin/{branch}" in remote_branches

        if branch_exists_locally:
            click.echo(f"📍 Branch '{branch}' exists locally, creating worktree...")
            ctx.run(f"git worktree add {worktree_path} {branch}")

        elif branch_exists_remotely:
            click.echo(
                f"🌐 Branch '{branch}' exists on remote, creating tracking worktree..."
            )
            # Create worktree and set up proper tracking
            ctx.run(f"git worktree add -b {branch} {worktree_path} origin/{branch}")

        else:
            # Create new branch
            if base and base.strip():
                click.echo(f"🆕 Creating new branch '{branch}' from '{base}'...")
                ctx.run(f"git worktree add -b {branch} {worktree_path} {base}")
            else:
                click.echo(f"🆕 Creating new branch '{branch}' from current HEAD...")
                ctx.run(f"git worktree add -b {branch} {worktree_path}")

        click.echo(f"✅ Worktree created successfully!")
        click.echo(f"📁 Location: {worktree_path}")
        click.echo(f"🔄 To switch: cd {worktree_path}")

        # Show branch tracking info
        try:
            tracking_info = ctx.run(
                f"cd {worktree_path} && git branch -vv | head -1", hide=True, warn=True
            )
            if tracking_info.ok:
                click.echo(f"🔗 Branch info: {tracking_info.stdout.strip()}")
        except:
            pass

    except Exception as e:
        click.echo(f"❌ Error creating worktree: {e}", err=True)
        click.echo("💡 Best practices:", err=True)
        click.echo("   • For existing remote branch: samosa git worktree add feature-branch", err=True)
        click.echo(
            "   • For new branch from main: samosa git worktree add new-feature --base main",
            err=True
        )
        click.echo("   • For new branch from current: samosa git worktree add new-feature", err=True)
        raise click.ClickException("Failed to create worktree")


@worktree.command("remove")
@click.argument("branch")
def worktree_remove(branch):
    """Remove a git worktree by branch name."""
    ctx = Context()
    
    # Get the current project directory name
    current_dir = Path.cwd()
    project_name = current_dir.name

    # Convert branch name to directory-safe format
    safe_branch = branch.replace("/", "-")

    # Create worktree directory name: project-name-branch
    worktree_name = f"{project_name}-{safe_branch}"

    # Path to worktree (one directory up)
    worktree_path = current_dir.parent / worktree_name

    click.echo(f"Removing worktree for branch '{branch}' at: {worktree_path}")

    try:
        # Check if worktree exists
        if not worktree_path.exists():
            click.echo(f"❌ Worktree directory not found: {worktree_path}", err=True)
            return

        # Remove the worktree
        ctx.run(f"git worktree remove {worktree_path}")

        click.echo(f"✅ Worktree removed successfully!")
        click.echo(f"🗑️  Removed: {worktree_path}")

    except Exception as e:
        click.echo(f"❌ Error removing worktree: {e}", err=True)
        # Try force remove if normal remove fails
        try:
            click.echo("🔄 Attempting force removal...")
            ctx.run(f"git worktree remove --force {worktree_path}")
            click.echo(f"✅ Worktree force removed successfully!")
        except Exception as fe:
            click.echo(f"❌ Force removal also failed: {fe}", err=True)
            raise click.ClickException("Failed to remove worktree")


@worktree.command("list")
def worktree_list():
    """List all git worktrees."""
    ctx = Context()
    click.echo("📂 Git Worktrees:")
    ctx.run("git worktree list")
