"""Task configuration and metadata."""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class TaskConfig:
    """Configuration for a task module."""

    # Module info
    module_name: str
    short_name: Optional[str] = None
    description: str = ""

    # Task behavior
    global_tasks: List[str] = None  # Tasks to expose globally (e.g., ['test', 'build'])
    namespaced_only: List[str] = None  # Tasks only available via namespace

    def __post_init__(self):
        """Initialize default values."""
        if self.global_tasks is None:
            self.global_tasks = []
        if self.namespaced_only is None:
            self.namespaced_only = []


# Task module configurations
TASK_CONFIGS: Dict[str, TaskConfig] = {
    "development": TaskConfig(
        module_name="development",
        short_name="dev",
        description="Development and testing tasks",
        global_tasks=[
            "test",
            "lint",
            "format",
            "typecheck",
            "check",
        ],  # Available globally
        namespaced_only=[],  # No dev-only tasks yet
    ),
    "build": TaskConfig(
        module_name="build",
        short_name="b",
        description="Build and packaging tasks",
        global_tasks=["build", "clean", "release"],  # Available globally
        namespaced_only=[],  # No build-only tasks yet
    ),
    "utils": TaskConfig(
        module_name="utils",
        short_name="u",
        description="Utility and helper tasks",
        global_tasks=["hello"],  # Only hello is global
        namespaced_only=[
            "info", 
            "env", 
            "install-alias", 
            "uninstall-alias",
            "install-completion",
            "uninstall-completion"
        ],  # info/env only via utils.info, u.info
    ),
    "git": TaskConfig(
        module_name="git",
        short_name="g",
        description="Git version control tasks",
        global_tasks=[],  # No global git tasks
        namespaced_only=[
            "status",
            "add",
            "commit",
            "push",
            "pull",
            "merge",
            "checkout",
            "browse",
        ],  # All via g.*
    ),
    "database": TaskConfig(
        module_name="database",
        short_name="db",
        description="Database management tasks",
        global_tasks=["migrate"],  # migrate available globally
        namespaced_only=["seed", "backup"],  # seed/backup only via db.*
    ),
}


def get_config(module_name: str) -> Optional[TaskConfig]:
    """Get configuration for a task module."""
    return TASK_CONFIGS.get(module_name)


def get_all_configs() -> Dict[str, TaskConfig]:
    """Get all task configurations."""
    return TASK_CONFIGS


def is_global_task(module_name: str, task_name: str) -> bool:
    """Check if a task should be available globally."""
    config = get_config(module_name)
    return config and task_name in config.global_tasks


def is_namespaced_only(module_name: str, task_name: str) -> bool:
    """Check if a task is only available via namespace."""
    config = get_config(module_name)
    return config and task_name in config.namespaced_only


def get_short_name(module_name: str) -> Optional[str]:
    """Get short name for a module (e.g., 'b' for 'build')."""
    config = get_config(module_name)
    return config.short_name if config else None
