"""Utility classes and functions for samosa CLI."""

import click


class AliasedGroup(click.Group):
    """A Click Group that supports command aliases and shows them in help as 'command (alias)'."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._aliases = {}

    def add_command_with_aliases(self, cmd, name, aliases=None):
        """Add a command with aliases."""
        self.add_command(cmd, name)
        if aliases:
            for alias in aliases:
                self._aliases[alias] = name

    def get_command(self, ctx, cmd_name):
        """Get command, resolving aliases to actual command names."""
        # Check if it's an alias first
        if cmd_name in self._aliases:
            cmd_name = self._aliases[cmd_name]
        return super().get_command(ctx, cmd_name)

    def list_commands(self, ctx):
        """List commands (without aliases to avoid completion duplicates)."""
        return super().list_commands(ctx)

    def format_commands(self, ctx, formatter):
        """Custom format showing aliases like 'command (alias1, alias2)'."""
        commands = []
        seen = set()

        for subcommand in self.list_commands(ctx):
            if subcommand in seen:
                continue
            cmd = self.get_command(ctx, subcommand)
            if cmd is None or cmd.hidden:
                continue

            # Find aliases for this command
            aliases = [
                alias for alias, target in self._aliases.items() if target == subcommand
            ]

            if aliases:
                name = f"{subcommand} ({', '.join(sorted(aliases))})"
            else:
                name = subcommand

            commands.append((name, cmd.get_short_help_str()))
            seen.add(subcommand)
            # Mark aliases as seen to avoid duplicates
            for alias in aliases:
                seen.add(alias)

        if commands:
            with formatter.section("Commands"):
                formatter.write_dl(commands)
