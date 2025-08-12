"""Local/project-specific commands."""

from samosa.plugins import get_local_command_group

# Get the dynamically generated local command group
local = get_local_command_group()
