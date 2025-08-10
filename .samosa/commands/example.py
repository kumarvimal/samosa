"""Example project-specific commands."""

import click

# project_context is injected by the samosa plugin system
project_context = None  # type: ignore


@click.group()
def deploy():
    """Deployment commands for this project."""


@deploy.command()
@click.argument("environment", type=click.Choice(["dev", "staging", "prod"]))
def app(environment):
    """Deploy application to specified environment."""
    # Access project context

    click.echo(f"🚀 Deploying to {environment}...")
    click.echo(f"📁 Project root: {project_context.project_root}")

    # Example: run deployment commands
    # ctx.run(f"docker build -t myapp:{environment} .")
    # ctx.run(f"kubectl apply -f k8s/{environment}/")

    click.echo(f"✅ Deployed to {environment}!")


@click.command()
def test():
    """Run project-specific tests."""

    click.echo("🧪 Running project tests...")
    # ctx.run("python -m pytest tests/")
    click.echo("✅ Tests completed!")


@click.command()
def setup():
    """Setup project development environment."""

    click.echo("🔧 Setting up development environment...")
    # ctx.run("pip install -r requirements.txt")
    # ctx.run("pre-commit install")
    click.echo("✅ Development environment ready!")
