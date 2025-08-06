"""Git-related tasks."""

import os
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
        ssh_match = re.match(r'git@github\.com:([^/]+)/(.+)\.git$', remote_url)
        if ssh_match:
            user, repo = ssh_match.groups()
            github_url = f"https://github.com/{user}/{repo}"
            
        # Handle HTTPS format: https://github.com/user/repo.git
        elif re.match(r'https://github\.com/([^/]+)/(.+?)\.git$', remote_url):
            https_match = re.match(r'https://github\.com/([^/]+)/(.+?)\.git$', remote_url)
            user, repo = https_match.groups()
            github_url = f"https://github.com/{user}/{repo}"
            
        # Handle HTTPS without .git: https://github.com/user/repo
        elif re.match(r'https://github\.com/([^/]+)/([^/]+)/?$', remote_url):
            https_no_git_match = re.match(r'https://github\.com/([^/]+)/([^/]+)/?$', remote_url)
            user, repo = https_no_git_match.groups()
            github_url = f"https://github.com/{user}/{repo}"
            
        if github_url:
            print(f"🌐 Opening: {github_url}")
            webbrowser.open(github_url)
            print("✅ Repository opened in browser!")
        else:
            print(f"❌ Could not parse GitHub URL from: {remote_url}")
            print("💡 Supported formats: git@github.com:user/repo.git or https://github.com/user/repo.git")
            
    except Exception as e:
        print(f"❌ Error opening repository: {e}")
        print("💡 Make sure you're in a git repository with a GitHub remote")


# Worktree subcommands
@task
def worktree_add(ctx, branch):
    """Create a git worktree one directory up with project-name-branch format.

    Args:
        branch: Branch name (e.g., feat/some-feature)
    """
    # Get the current project directory name
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

    # Create the worktree
    try:
        # First check if branch exists remotely and fetch if needed
        result = ctx.run("git branch -r", hide=True)
        remote_branches = result.stdout

        if f"origin/{branch}" in remote_branches:
            print(f"Branch '{branch}' exists on remote, creating worktree...")
            ctx.run(f"git worktree add {worktree_path} {branch}")
        else:
            print(
                f"Branch '{branch}' not found on remote, creating new branch and worktree..."
            )
            ctx.run(f"git worktree add -b {branch} {worktree_path}")

        print(f"✅ Worktree created successfully!")
        print(f"📁 Location: {worktree_path}")
        print(f"🔄 To switch: cd {worktree_path}")

    except Exception as e:
        print(f"❌ Error creating worktree: {e}")
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


# Create worktree collection
worktree_collection = Collection("worktree")
worktree_collection.add_task(worktree_add, "add")
worktree_collection.add_task(worktree_remove, "remove")
worktree_collection.add_task(worktree_list, "list")

# Create main git collection that includes worktree as a sub-collection
git_collection = Collection()
git_collection.add_task(status)
git_collection.add_task(add)
git_collection.add_task(commit)
git_collection.add_task(push)
git_collection.add_task(pull)
git_collection.add_task(merge)
git_collection.add_task(checkout)
git_collection.add_task(browse)
git_collection.add_collection(worktree_collection)
