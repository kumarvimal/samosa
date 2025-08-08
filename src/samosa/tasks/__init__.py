"""Samosa task collections with auto-discovery and optional configuration."""

import importlib
import importlib.util
from pathlib import Path

from invoke import Collection

from .config import get_all_configs


def discover_task_modules():
    """Auto-discover all task modules in the tasks directory."""
    discovered_modules = {}

    current_dir = Path(__file__).parent

    for py_file in current_dir.glob("*.py"):
        module_name = py_file.stem

        if module_name.startswith("_") or module_name in ["config"]:
            continue

        try:
            module = importlib.import_module(f".{module_name}", package="samosa.tasks")
            discovered_modules[module_name] = module
        except ImportError as e:
            print(f"Warning: Could not import task module '{module_name}': {e}")
            continue

    return discovered_modules


def create_main_collection() -> Collection:
    """Create the main task collection with auto-discovery."""
    main_collection = Collection()

    configs = get_all_configs()
    discovered_modules = discover_task_modules()

    # Track added global task names to avoid conflicts
    global_task_names = set()

    # Process all discovered modules
    for module_name, module in discovered_modules.items():
        # Get configuration if it exists
        config = configs.get(module_name)

        # Add global tasks if configured
        if config and config.global_tasks:
            for task_name in config.global_tasks:
                if hasattr(module, task_name):
                    task = getattr(module, task_name)
                    main_collection.add_task(task, name=task_name)
                    global_task_names.add(task_name)

        # Add as namespaced collection, avoiding conflicts with global tasks
        collection_name = module_name
        if collection_name not in global_task_names:
            # Check if module has a custom collection (e.g., git_collection)
            custom_collection = getattr(module, f"{module_name}_collection", None)
            if custom_collection:
                main_collection.add_collection(custom_collection, name=collection_name)
            else:
                main_collection.add_collection(module, name=collection_name)

        # Add short namespace if configured
        if config and config.short_name:
            short_name = config.short_name
            if short_name not in global_task_names:
                # Check if module has a custom collection for short name too
                custom_collection = getattr(module, f"{module_name}_collection", None)
                if custom_collection:
                    main_collection.add_collection(custom_collection, name=short_name)
                else:
                    main_collection.add_collection(module, name=short_name)
        # If no config, create a simple short name (first letter)
        elif not config and len(module_name) > 1:
            short_name = module_name[0]
            # Make sure short name doesn't conflict with existing short names or global tasks
            existing_short_names = {
                c.short_name for c in configs.values() if c.short_name
            }
            if (
                short_name not in existing_short_names
                and short_name not in global_task_names
            ):
                # Check if module has a custom collection for auto-discovered short name
                custom_collection = getattr(module, f"{module_name}_collection", None)
                if custom_collection:
                    main_collection.add_collection(custom_collection, name=short_name)
                else:
                    main_collection.add_collection(module, name=short_name)

    return main_collection


main_collection = create_main_collection()
