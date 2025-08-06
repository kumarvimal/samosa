"""CLI interface for samosa."""

import sys
from typing import Any

import click
from invoke import Collection, Config, Context


def load_invoke_collection() -> Collection:
    """Load the invoke tasks collection from packaged tasks."""
    try:
        # Import the packaged tasks collection
        from samosa.tasks import main_collection

        return main_collection
    except ImportError as e:
        raise RuntimeError(f"Could not load samosa tasks: {e}") from e


@click.group()
@click.version_option(version="0.1.0", prog_name="samosa")
@click.pass_context
def main(ctx: click.Context) -> None:
    """Samosa - A Python CLI tool with invoke integration."""
    # Store invoke collection in context for subcommands
    try:
        ctx.ensure_object(dict)
        ctx.obj["collection"] = load_invoke_collection()
        ctx.obj["config"] = Config()  # Use default config
    except Exception as e:
        click.echo(f"Error loading invoke tasks: {e}", err=True)
        sys.exit(1)


# Override the help formatter to use custom names
def format_commands(self, ctx, formatter):
    """Custom formatter that uses _help_name if available."""
    commands = []
    for subcommand in self.list_commands(ctx):
        cmd = self.get_command(ctx, subcommand)
        if cmd is None:
            continue
        if cmd.hidden:
            continue

        # Use custom help name if available
        help_name = getattr(cmd, "_help_name", subcommand)
        commands.append((help_name, cmd))

    if commands:
        with formatter.section("Commands"):
            formatter.write_dl(
                [(name, cmd.get_short_help_str()) for name, cmd in commands]
            )


# Apply the custom formatter to the main group
main.format_commands = format_commands.__get__(main, click.Group)


def create_invoke_command(
    task_name: str, task_obj: Any, namespace_collection: Any = None
) -> click.Command:
    """Create a click command from an invoke task."""

    def command_func(**kwargs: Any) -> None:
        ctx = click.get_current_context()
        collection = ctx.obj["collection"]
        config = ctx.obj["config"]

        # Create invoke context
        invoke_ctx = Context(config=config)

        # Get the task from appropriate collection
        if namespace_collection:
            task = namespace_collection[task_name]
        else:
            task = collection[task_name]

        # Filter kwargs to only include task parameters
        task_kwargs = {}
        if hasattr(task, "get_arguments"):
            # Get task argument names
            for arg in task.get_arguments():
                arg_name = arg.name.replace("-", "_")
                if arg_name in kwargs:
                    task_kwargs[arg_name] = kwargs[arg_name]

        try:
            # Execute the task
            task(invoke_ctx, **task_kwargs)
        except Exception as e:
            click.echo(f"Error executing task '{task_name}': {e}", err=True)
            sys.exit(1)

    # Get task docstring for help (mimic invoke --list behavior)
    help_text = None
    if hasattr(task_obj, "body") and hasattr(task_obj.body, "__doc__"):
        docstring = task_obj.body.__doc__
        if docstring:
            # Extract first line of docstring (like invoke --list does)
            help_text = docstring.strip().split("\n")[0]

    # Create click command with task arguments as options
    cmd = click.command(name=task_name, help=help_text)(command_func)

    # Add task arguments as click options
    if hasattr(task_obj, "get_arguments"):
        for arg in reversed(task_obj.get_arguments()):  # Reverse to maintain order
            arg_name = arg.name.replace("-", "_")

            if hasattr(arg, "default") and arg.default is not None:
                # Argument with default value becomes an option
                cmd = click.option(
                    f"--{arg.name}",
                    arg_name,
                    default=arg.default,
                    help=getattr(arg, "help", None),
                )(cmd)
            else:
                # Required argument becomes a click argument
                cmd = click.argument(arg_name)(cmd)

    return cmd


# Dynamically register invoke tasks and collections as click commands
def register_invoke_commands() -> None:
    """Register all invoke tasks and namespaced collections as click commands."""
    try:
        collection = load_invoke_collection()

        # Register individual tasks (global tasks)
        for task_name, task_obj in collection.tasks.items():
            # Skip private/internal tasks
            if task_name.startswith("_"):
                continue

            cmd = create_invoke_command(task_name, task_obj)
            main.add_command(cmd)

        # Register namespace collections as subcommands
        from .tasks import discover_task_modules
        from .tasks.config import get_all_configs

        configs = get_all_configs()
        discovered_modules = discover_task_modules()

        # Track processed collections to avoid duplicates
        processed_collections = set()

        # First, register configured modules
        for module_name, module_config in configs.items():
            # Find the collection for this module (try short name first)
            ns_collection = None
            if (
                module_config.short_name
                and module_config.short_name in collection.collections
            ):
                ns_collection = collection.collections[module_config.short_name]
                processed_collections.add(module_config.short_name)
            elif module_name in collection.collections:
                ns_collection = collection.collections[module_name]
                processed_collections.add(module_name)

            if ns_collection:
                # Create the primary group with full name that shows both names in help
                primary_group = create_namespace_group(
                    module_name, ns_collection, module_config, is_primary=True
                )
                main.add_command(primary_group)

                # Register short name as a hidden alias (same group, different name)
                if module_config.short_name and module_config.short_name != module_name:
                    # Create an alias group that's hidden from help
                    alias_group = create_namespace_group(
                        module_config.short_name,
                        ns_collection,
                        module_config,
                        is_primary=False,
                        hidden=True,
                    )
                    main.add_command(alias_group)

        # Then, register any auto-discovered modules that weren't configured
        for module_name in discovered_modules:
            if module_name not in processed_collections:
                # This module was auto-discovered but not configured
                ns_collection = collection.collections.get(module_name)
                if ns_collection:
                    # Create primary group with full module name
                    primary_group = create_namespace_group(
                        module_name, ns_collection, None, is_primary=True
                    )
                    main.add_command(primary_group)
                    processed_collections.add(module_name)

                    # Check if there's also a short name collection for this module
                    short_name = module_name[0] if len(module_name) > 1 else None
                    if (
                        short_name
                        and short_name in collection.collections
                        and short_name not in processed_collections
                    ):
                        # Create alias group for short name
                        short_ns_collection = collection.collections[short_name]
                        alias_group = create_namespace_group(
                            short_name,
                            short_ns_collection,
                            None,
                            is_primary=False,
                            hidden=True,
                        )
                        main.add_command(alias_group)
                        processed_collections.add(short_name)

                        # Update help name for primary group to show both
                        primary_group._help_name = f"{module_name}({short_name})"

    except Exception:
        # If we can't load tasks, just continue with base CLI
        pass


def create_namespace_group(
    ns_name: str,
    ns_collection: Any,
    config: Any = None,
    is_primary: bool = True,
    hidden: bool = False,
) -> click.Group:
    """Create a click group for a namespace collection."""

    # Get description
    description = config.description if config else f"Commands for {ns_name} namespace"

    # Create the group
    @click.group(name=ns_name, help=description, hidden=hidden)
    def ns_group():
        pass

    # For primary commands, store the display name for help formatting
    if (
        is_primary
        and config
        and config.short_name
        and config.short_name != config.module_name
    ):
        ns_group._help_name = f"{config.module_name}({config.short_name})"
    else:
        ns_group._help_name = ns_name

    # Add all tasks in this namespace as subcommands
    for task_name, task_obj in ns_collection.tasks.items():
        if task_name.startswith("_"):
            continue

        cmd = create_invoke_command(task_name, task_obj, ns_collection)
        ns_group.add_command(cmd)

    return ns_group


# Register commands at module level
register_invoke_commands()


if __name__ == "__main__":
    main()
