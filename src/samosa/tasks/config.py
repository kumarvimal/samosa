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
    global_tasks: List[str] = None  # Tasks to expose globally (e.g., ['test', 'lint'])

    def __post_init__(self):
        """Initialize default values."""
        if self.global_tasks is None:
            self.global_tasks = []


TASK_CONFIGS: Dict[str, TaskConfig] = {
    "development": TaskConfig(
        module_name="development",
        short_name="dev",
        description="Development and testing tasks",
        global_tasks=[],
    ),
    "utils": TaskConfig(
        module_name="utils",
        short_name="u",
        description="Utility and helper tasks",
        global_tasks=["hello"],
    ),
    "git": TaskConfig(
        module_name="git",
        short_name="g",
        description="Git version control tasks",
        global_tasks=[],
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


def get_short_name(module_name: str) -> Optional[str]:
    """Get short name for a module (e.g., 'b' for 'build')."""
    config = get_config(module_name)
    return config.short_name if config else None
