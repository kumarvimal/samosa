"""Database-related tasks (not configured in config.py yet)."""

from invoke import task


@task
def migrate(ctx):
    """Run database migrations."""
    print("Running database migrations...")
    ctx.run("echo 'Migration complete!'")


@task
def seed(ctx):
    """Seed the database with initial data."""
    print("Seeding database...")
    ctx.run("echo 'Database seeded!'")


@task
def backup(ctx, filename="backup.sql"):
    """Create a database backup.

    Args:
        filename: Backup file name (default: backup.sql)
    """
    print(f"Creating database backup: {filename}")
    ctx.run(f"echo 'Backup created: {filename}'")
