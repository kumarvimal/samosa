"""Git-related tasks."""

from invoke import task


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
