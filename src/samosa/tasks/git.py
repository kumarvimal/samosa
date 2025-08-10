"""Git-related tasks."""

import os
from datetime import datetime
from pathlib import Path
from invoke import task, Collection


@task
def status(ctx):
    """Show git status."""
    ctx.run("git status")


@task
def add(ctx, files="."):
    """Add files to git staging.

    Args:
        files: Files to add (default: all files)
    """
    ctx.run(f"git add {files}")


@task
def commit(ctx, message):
    """Create a git commit.

    Args:
        message: Commit message
    """
    ctx.run(f'git commit -m "{message}"')


@task
def push(ctx, remote="origin", branch=None):
    """Push changes to remote.

    Args:
        remote: Remote name (default: origin)
        branch: Branch to push (default: current branch)
    """
    if branch:
        ctx.run(f"git push {remote} {branch}")
    else:
        ctx.run(f"git push {remote}")


@task
def pull(ctx, remote="origin", branch=None):
    """Pull changes from remote.

    Args:
        remote: Remote name (default: origin)
        branch: Branch to pull (default: current branch)
    """
    if branch:
        ctx.run(f"git pull {remote} {branch}")
    else:
        ctx.run(f"git pull {remote}")


@task
def merge(ctx, branch):
    """Merge a branch into current branch.

    Args:
        branch: Branch to merge
    """
    ctx.run(f"git merge {branch}")


@task
def checkout(ctx, branch, create=False):
    """Checkout a branch.

    Args:
        branch: Branch name
        create: Create new branch if it doesn't exist
    """
    if create:
        ctx.run(f"git checkout -b {branch}")
    else:
        ctx.run(f"git checkout {branch}")


@task
def sync(ctx, remote="origin", main_branch=""):
    """Sync current branch with remote main.
    
    Fetches latest changes and merges remote main into current branch.
    Auto-detects the default branch if not specified.
    
    Args:
        remote: Remote name (default: origin)
        main_branch: Main branch name (auto-detected if not provided)
    """
    try:
        # Get current branch name
        result = ctx.run("git branch --show-current", hide=True)
        current_branch = result.stdout.strip()
        
        if not current_branch:
            print("❌ Could not determine current branch")
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
        
        print(f"🔄 Syncing branch '{current_branch}' with {remote}/{main_branch}...")
        
        print("📥 Fetching latest changes...")
        ctx.run(f"git fetch {remote}")
        
        print(f"🔀 Rebasing {current_branch} onto {remote}/{main_branch}...")
        ctx.run(f"git rebase {remote}/{main_branch}")
        
        print("✅ Branch synced successfully!")
        
    except Exception as e:
        print(f"❌ Error syncing branch: {e}")
        print("💡 Make sure you have no uncommitted changes and the remote exists")
        raise


@task
def browse(ctx):
    """Open current git repository in GitHub in the browser."""
    import re
    import webbrowser

    try:
        # Get the remote URL
        result = ctx.run("git remote get-url origin", hide=True)
        remote_url = result.stdout.strip()

        if not remote_url:
            print("❌ No remote 'origin' found")
            return

        print(f"🔍 Found remote URL: {remote_url}")

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
            print(f"🌐 Opening: {github_url}")
            webbrowser.open(github_url)
            print("✅ Repository opened in browser!")
        else:
            print(f"❌ Could not parse GitHub URL from: {remote_url}")
            print(
                "💡 Supported formats: git@github.com:user/repo.git or https://github.com/user/repo.git"
            )

    except Exception as e:
        print(f"❌ Error opening repository: {e}")
        print("💡 Make sure you're in a git repository with a GitHub remote")


@task
def backup_add(ctx):
    """Create a backup branch from the current branch."""
    try:
        # Get current branch name
        result = ctx.run("git branch --show-current", hide=True)
        current_branch = result.stdout.strip()
        
        if not current_branch:
            print("❌ Could not determine current branch")
            return
        
        now = datetime.now()
        timestamp = now.strftime("%H-%M-%S_%d-%m-%Y")
        backup_branch = f"backup/{current_branch}-{timestamp}"

        response = input("❓ Create backup branch? [y/N]: ").strip().lower()
        
        if response in ['y', 'yes']:
            print(f"💾 Creating backup branch: {backup_branch}")
            ctx.run(f"git branch {backup_branch}")
            print(f"✅ Backup branch '{backup_branch}' created successfully!")
        else:
            print("❌ Backup creation cancelled")
        
    except Exception as e:
        print(f"❌ Error creating backup branch: {e}")
        print("💡 Make sure you're in a git repository and have commits")
        raise


@task
def backup_list(ctx):
    """List all backup branches for the current branch."""
    try:
        # Get current branch name
        result = ctx.run("git branch --show-current", hide=True)
        current_branch = result.stdout.strip()
        
        if not current_branch:
            print("❌ Could not determine current branch")
            return
        
        print(f"🔍 Backup branches for '{current_branch}':")
        
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
                print(f"  📦 {backup}")
            print(f"\n✅ Found {len(backups)} backup(s)")
        else:
            print(f"  💭 No backup branches found for '{current_branch}'")
            
    except Exception as e:
        print(f"❌ Error listing backup branches: {e}")
        print("💡 Make sure you're in a git repository")
        raise


@task
def backup_delete(ctx, mode="", branch=""):
    """Delete backup branches for the current branch.
    
    Args:
        mode: 'all' to delete all backup branches, or leave empty for specific branch deletion
        branch: Specific backup branch name to delete (without backup/ prefix)
    """
    try:
        # Get current branch name
        result = ctx.run("git branch --show-current", hide=True)
        current_branch = result.stdout.strip()
        
        if not current_branch:
            print("❌ Could not determine current branch")
            return
        
        if branch:
            # Failsafe: ensure we only delete backup branches
            if not branch.startswith("backup/"):
                # If user provided branch without backup/ prefix, add it
                if "/" not in branch:
                    backup_branch = f"backup/{branch}"
                else:
                    # If user provided full branch name, ensure it starts with backup/
                    if not branch.startswith("backup/"):
                        print(f"❌ Safety check failed: Can only delete backup branches (must start with 'backup/')")
                        print(f"💡 You provided: '{branch}' - this doesn't look like a backup branch")
                        print("💡 Use 'samosa git backup list' to see available backup branches")
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
                print(f"❌ Backup branch '{backup_branch}' not found")
                print("💡 Use 'samosa git backup list' to see available backups")
                return
            
            print(f"🗑️  Deleting backup branch: {backup_branch}")
            
            # Ask for confirmation with red warning
            print(f"\n\033[91m⚠️  WARNING: This will permanently delete backup branch '{backup_branch}'!\033[0m")
            response = input(f"\033[91m❓ Are you sure you want to delete this backup branch? [y/N]: \033[0m").strip().lower()
            
            if response in ['y', 'yes']:
                try:
                    # Final safety check before deletion
                    if not backup_branch.startswith("backup/"):
                        print(f"❌ SAFETY ABORT: Refusing to delete non-backup branch '{backup_branch}'")
                        return
                    
                    ctx.run(f"git branch -D {backup_branch}")
                    print(f"✅ Successfully deleted backup branch '{backup_branch}'")
                except Exception as e:
                    print(f"❌ Failed to delete {backup_branch}: {e}")
            else:
                print("❌ Backup deletion cancelled")
                
        elif mode == "all":
            # Delete all backup branches for current branch
            print(f"🗑️  Deleting all backup branches for '{current_branch}'...")
            
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
                print(f"  💭 No local backup branches found for '{current_branch}'")
                return
            
            print(f"📋 Found {len(local_backups)} backup branch(es) to delete:")
            for backup in sorted(local_backups):
                print(f"  📦 {backup}")
            
            # Ask for confirmation with red warning
            print(f"\n\033[91m⚠️  WARNING: This will permanently delete {len(local_backups)} backup branch(es)!\033[0m")
            response = input(f"\033[91m❓ Are you sure you want to delete all backup branches? [y/N]: \033[0m").strip().lower()
            
            if response in ['y', 'yes']:
                deleted_count = 0
                for backup in local_backups:
                    try:
                        # Final safety check before deletion
                        if not backup.startswith("backup/"):
                            print(f"  ❌ SAFETY ABORT: Skipping non-backup branch '{backup}'")
                            continue
                        
                        ctx.run(f"git branch -D {backup}")
                        print(f"  🗑️  Deleted: {backup}")
                        deleted_count += 1
                    except Exception as e:
                        print(f"  ❌ Failed to delete {backup}: {e}")
                
                if deleted_count > 0:
                    print(f"✅ Successfully deleted {deleted_count}/{len(local_backups)} backup branch(es)")
                else:
                    print("❌ No backup branches were deleted")
            else:
                print("❌ Backup deletion cancelled")
        else:
            # No flags provided, show help
            print("❌ Please specify either --mode all to delete all backups or provide a branch name")
            print("💡 Usage:")
            print("   samosa git backup delete --mode all")
            print("   samosa git backup delete --branch main-21-36-47_08-08-2025")
            print("   samosa git backup list  # to see available backups")
            
    except Exception as e:
        print(f"❌ Error deleting backup branches: {e}")
        print("💡 Make sure you're in a git repository")
        raise



@task
def worktree_add(ctx, branch, base="", fetch=True):
    """Create a git worktree one directory up with project-name-branch format.

    Args:
        branch: Branch name (e.g., feat/some-feature)
        base: Base branch/commit to create new branch from (default: current branch)
        fetch: Fetch latest remote changes before creating worktree (default: True)
    """
    current_dir = Path.cwd()
    project_name = current_dir.name

    # Convert branch name to directory-safe format
    # feat/some-feature -> feat-some-feature
    safe_branch = branch.replace("/", "-")

    # Create worktree directory name: project-name-branch
    worktree_name = f"{project_name}-{safe_branch}"

    # Path to create worktree (one directory up)
    worktree_path = current_dir.parent / worktree_name

    print(f"Creating worktree for branch '{branch}' at: {worktree_path}")

    try:
        # Fetch latest changes if requested
        if fetch:
            print("🔄 Fetching latest changes...")
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
            print(f"📍 Branch '{branch}' exists locally, creating worktree...")
            ctx.run(f"git worktree add {worktree_path} {branch}")

        elif branch_exists_remotely:
            print(
                f"🌐 Branch '{branch}' exists on remote, creating tracking worktree..."
            )
            # Create worktree and set up proper tracking
            ctx.run(f"git worktree add -b {branch} {worktree_path} origin/{branch}")

        else:
            # Create new branch
            if base and base.strip():
                print(f"🆕 Creating new branch '{branch}' from '{base}'...")
                ctx.run(f"git worktree add -b {branch} {worktree_path} {base}")
            else:
                print(f"🆕 Creating new branch '{branch}' from current HEAD...")
                ctx.run(f"git worktree add -b {branch} {worktree_path}")

        print(f"✅ Worktree created successfully!")
        print(f"📁 Location: {worktree_path}")
        print(f"🔄 To switch: cd {worktree_path}")

        # Show branch tracking info
        try:
            tracking_info = ctx.run(
                f"cd {worktree_path} && git branch -vv | head -1", hide=True, warn=True
            )
            if tracking_info.ok:
                print(f"🔗 Branch info: {tracking_info.stdout.strip()}")
        except:
            pass

    except Exception as e:
        print(f"❌ Error creating worktree: {e}")
        print("💡 Best practices:")
        print("   • For existing remote branch: samosa g worktree add feature-branch")
        print(
            "   • For new branch from main: samosa g worktree add new-feature --base main"
        )
        print("   • For new branch from current: samosa g worktree add new-feature")
        raise


@task
def worktree_remove(ctx, branch):
    """Remove a git worktree by branch name.

    Args:
        branch: Branch name of the worktree to remove (e.g., feat/some-feature)
    """
    # Get the current project directory name
    current_dir = Path.cwd()
    project_name = current_dir.name

    # Convert branch name to directory-safe format
    safe_branch = branch.replace("/", "-")

    # Create worktree directory name: project-name-branch
    worktree_name = f"{project_name}-{safe_branch}"

    # Path to worktree (one directory up)
    worktree_path = current_dir.parent / worktree_name

    print(f"Removing worktree for branch '{branch}' at: {worktree_path}")

    try:
        # Check if worktree exists
        if not worktree_path.exists():
            print(f"❌ Worktree directory not found: {worktree_path}")
            return

        # Remove the worktree
        ctx.run(f"git worktree remove {worktree_path}")

        print(f"✅ Worktree removed successfully!")
        print(f"🗑️  Removed: {worktree_path}")

    except Exception as e:
        print(f"❌ Error removing worktree: {e}")
        # Try force remove if normal remove fails
        try:
            print("🔄 Attempting force removal...")
            ctx.run(f"git worktree remove --force {worktree_path}")
            print(f"✅ Worktree force removed successfully!")
        except Exception as fe:
            print(f"❌ Force removal also failed: {fe}")
            raise


@task
def worktree_list(ctx):
    """List all git worktrees."""
    print("📂 Git Worktrees:")
    ctx.run("git worktree list")


# Create backup collection
backup_collection = Collection("backup")
backup_collection.add_task(backup_add, "add")
backup_collection.add_task(backup_list, "list")
backup_collection.add_task(backup_delete, "delete")

# Create worktree collection
worktree_collection = Collection("worktree")
worktree_collection.add_task(worktree_add, "add")
worktree_collection.add_task(worktree_remove, "remove")
worktree_collection.add_task(worktree_list, "list")

# Create main git collection that includes backup and worktree as sub-collections
git_collection = Collection()
git_collection.add_task(status)
git_collection.add_task(add)
git_collection.add_task(commit)
git_collection.add_task(push)
git_collection.add_task(pull)
git_collection.add_task(merge)
git_collection.add_task(checkout)
git_collection.add_task(sync)
git_collection.add_task(browse)
git_collection.add_collection(backup_collection)
git_collection.add_collection(worktree_collection)
