"""
MediaPlanPy Examples - Load Workspace

This script demonstrates how to load workspace configurations using MediaPlanPy SDK v3.0.
Workspaces can be loaded in three different ways depending on your use case.

v3.0 Features Demonstrated:
- WorkspaceManager.load() three loading patterns
- Workspace version validation (v3.0 required)
- Schema version enforcement
- Automatic configuration migration for deprecated fields
- Workspace status checking (active/inactive)

Prerequisites:
- MediaPlanPy SDK v3.0.0+ installed
- Workspace configurations created (see examples_create_workspace.py)

How to Run:
1. First run examples_create_workspace.py to create test workspaces
2. Open this file in your IDE
3. Run the entire script: python examples_load_workspace.py
4. Or run individual functions by calling them from __main__

Next Steps After Running:
- Use the loaded WorkspaceManager to create media plans
- Access storage backend via manager.get_storage_backend()
- Query workspace contents via manager.list_campaigns(), etc.
"""

import os
import json
from pathlib import Path
from datetime import datetime

from mediaplanpy.workspace import WorkspaceManager
from mediaplanpy import __schema_version__


# ============================================================================
# USER CONFIGURATION
# Update these values after running examples_create_workspace.py
# ============================================================================

# Example 1: Load by Path
# Copy the "Settings file" path from examples_create_workspace.py output
WORKSPACE_SETTINGS_PATH = "C:/mediaplanpy/workspace_b92ee88b_settings.json"

# Example 2: Load by Workspace ID
# Copy the "Workspace ID" from examples_create_workspace.py output
WORKSPACE_ID = "workspace_b92ee88b"

# ============================================================================


def get_configuration_value(config_name, prompt_message, example_value):
    """
    Get configuration value - either from constant or interactive user input.

    Args:
        config_name: Name of the configuration constant (e.g., 'WORKSPACE_SETTINGS_PATH')
        prompt_message: Message to show when prompting user
        example_value: Example value to show user

    Returns:
        Configuration value or None if user chooses to skip
    """
    # Get the current value from constants
    if config_name == 'WORKSPACE_SETTINGS_PATH':
        current_value = WORKSPACE_SETTINGS_PATH
    elif config_name == 'WORKSPACE_ID':
        current_value = WORKSPACE_ID
    else:
        return None

    # If already configured (not a placeholder), return it
    if "xxxxxxxx" not in current_value:
        return current_value

    # Prompt user for input
    print(f"\nConfiguration needed: {config_name}")
    print(f"Example: {example_value}")
    print(f"\nOptions:")
    print(f"  1. Enter the value now (paste from examples_create_workspace.py output)")
    print(f"  2. Type 'skip' to skip this example")
    print(f"  3. Update the constant at the top of this file and re-run")

    user_input = input(f"\n{prompt_message}: ").strip()

    if user_input.lower() == 'skip':
        print("Skipping this example.")
        return None

    if user_input:
        return user_input
    else:
        print("No value provided. Skipping this example.")
        return None


def load_by_path():
    """
    Load workspace by direct file path.

    Use Case:
        When you have the full path to a workspace settings file.
        This is the most straightforward loading method.

    v3.0 Features:
        - Direct file loading with workspace_path parameter
        - Schema version validation (must be v3.0)
        - Automatic migration of deprecated fields
        - Workspace status check with warning if inactive

    Returns:
        Loaded workspace configuration dictionary or None if config not provided

    Prerequisites:
        - Run examples_create_workspace.py first to create workspaces
        - Either update WORKSPACE_SETTINGS_PATH at top of file, or provide value when prompted
    """
    print("\n" + "="*60)
    print("Loading Workspace by Path")
    print("="*60)

    # Get configuration value (from constant or user input)
    settings_path = get_configuration_value(
        'WORKSPACE_SETTINGS_PATH',
        'Enter workspace settings file path',
        'C:/mediaplanpy/workspace_abc123_settings.json'
    )

    if settings_path is None:
        return None

    print(f"\nAttempting to load: {settings_path}")

    # Load by direct path - this is the simplest method
    manager = WorkspaceManager()
    config = manager.load(workspace_path=settings_path)

    print(f"\n✓ Successfully loaded workspace by path")
    print(f"\nWorkspace Details:")
    print(f"  - Workspace ID: {config['workspace_id']}")
    print(f"  - Workspace name: {config['workspace_name']}")
    print(f"  - Schema version: {config['workspace_settings']['schema_version']}")
    print(f"  - Storage mode: {config['storage']['mode']}")
    print(f"  - Status: {config['workspace_status']}")
    print(f"  - Is loaded: {manager.is_loaded}")

    print(f"\nStorage Configuration:")
    if config['storage']['mode'] == 'local':
        print(f"  - Base path: {config['storage']['local']['base_path']}")
    elif config['storage']['mode'] == 's3':
        print(f"  - S3 bucket: {config['storage']['s3']['bucket']}")
        print(f"  - S3 region: {config['storage']['s3']['region']}")

    print(f"\nNext Steps:")
    print(f"  1. Create media plans: MediaPlan.create(...)")
    print(f"  2. Save plans: plan.save(manager)")
    print(f"  3. Query workspace: manager.list_campaigns()")

    return config


def load_by_workspace_id():
    """
    Load workspace by workspace_id using automatic search.

    Use Case:
        When you know the workspace_id but not the exact file location.
        The load() method searches multiple standard locations automatically.

    v3.0 Features:
        - Automatic file location search using workspace_id
        - Searches: default directory, current directory, user directories
        - Schema version validation
        - Error with helpful search paths if not found

    Returns:
        Loaded workspace configuration dictionary or None if config not provided

    Prerequisites:
        - Run examples_create_workspace.py first to create workspaces
        - Either update WORKSPACE_ID at top of file, or provide value when prompted

    Note:
        The workspace_id search looks in these locations (in order):
        1. Default directory (C:/mediaplanpy on Windows, ~/mediaplanpy on Unix)
        2. Current working directory
        3. User config directories (~/.mediaplanpy or ~/.config/mediaplanpy)

        File names checked: {workspace_id}_settings.json or {workspace_id}.json
    """
    print("\n" + "="*60)
    print("Loading Workspace by ID")
    print("="*60)

    # Get configuration value (from constant or user input)
    workspace_id = get_configuration_value(
        'WORKSPACE_ID',
        'Enter workspace ID',
        'workspace_abc12345'
    )

    if workspace_id is None:
        return None

    print(f"\nAttempting to load workspace_id: {workspace_id}")
    print(f"Searching in standard locations...")

    # Load by workspace_id - this will search in standard locations
    manager = WorkspaceManager()
    config = manager.load(workspace_id=workspace_id)

    print(f"\n✓ Successfully loaded workspace by ID")
    print(f"\nWorkspace Details:")
    print(f"  - Workspace ID: {config['workspace_id']}")
    print(f"  - Workspace name: {config['workspace_name']}")
    print(f"  - Schema version: {config['workspace_settings']['schema_version']}")
    print(f"  - Storage mode: {config['storage']['mode']}")
    print(f"  - Status: {config['workspace_status']}")

    print(f"\nSearch Locations Checked:")
    print(f"  1. Default directory: C:/mediaplanpy/{workspace_id}_settings.json")
    print(f"  2. Current directory: ./{workspace_id}_settings.json")
    print(f"  3. User directories: ~/.mediaplanpy/{workspace_id}_settings.json")

    return config


def load_by_dict():
    """
    Load workspace from in-memory configuration dictionary.

    Use Case:
        Testing, dynamic configuration, non-file-based configs,
        programmatic workspace generation, or config from external sources.

    v3.0 Features:
        - In-memory workspace creation without files
        - Programmatic configuration building
        - Full schema validation on dictionary
        - Migration of deprecated fields

    Returns:
        Loaded workspace configuration dictionary

    Next Steps:
        - Useful for testing without file I/O
        - Can modify config dict before loading
        - Manager has no workspace_path (file-less operation)
        - Still fully functional for creating/loading media plans

    Note:
        This method is ideal for:
        - Unit testing
        - Dynamic configuration generation
        - Loading configs from databases or APIs
        - Temporary workspaces
    """
    print("\n" + "="*60)
    print("Loading Workspace from Dictionary")
    print("="*60)

    # Create config dict programmatically
    # This matches the structure of a workspace settings file
    config_dict = {
        "workspace_id": "test_dict_workspace",
        "workspace_name": "In-Memory Test Workspace",
        "workspace_status": "active",
        "environment": "testing",

        # Storage configuration
        "storage": {
            "mode": "local",
            "local": {
                "base_path": "C:/mediaplanpy/test_dict_workspace",  # Or ~/mediaplanpy on Unix
                "create_if_missing": True
            },
            "s3": {
                "bucket": "",
                "region": "",
                "prefix": "test_dict_workspace",
                "profile": "",
                "endpoint_url": "",
                "use_ssl": True
            }
        },

        # Workspace settings - MUST include schema version
        "workspace_settings": {
            "schema_version": __schema_version__,
            "last_upgraded": datetime.now().strftime("%Y-%m-%d"),
            "sdk_version_required": f"{__schema_version__.split('.')[0]}.0.x"
        },

        # Database configuration
        "database": {
            "enabled": False,
            "host": "localhost",
            "port": 5432,
            "database": "mediaplanpy",
            "schema": "public",
            "table_name": "media_plans",
            "username": "postgres",
            "password_env_var": "MEDIAPLAN_DB_PASSWORD",
            "ssl": False,
            "connection_timeout": 30,
            "auto_create_table": True
        },

        # Excel configuration
        "excel": {
            "enabled": True
        },

        # Google Sheets configuration
        "google_sheets": {
            "enabled": False
        },

        # Logging configuration
        "logging": {
            "level": "INFO"
        }
    }

    print("Created configuration dictionary with:")
    print(f"  - Workspace ID: {config_dict['workspace_id']}")
    print(f"  - Schema version: {config_dict['workspace_settings']['schema_version']}")
    print(f"  - Storage mode: {config_dict['storage']['mode']}")

    # Load from dict - no file I/O involved
    manager = WorkspaceManager()
    loaded_config = manager.load(config_dict=config_dict)

    print(f"\n✓ Successfully loaded workspace from dictionary")
    print(f"\nWorkspace Details:")
    print(f"  - Workspace name: {loaded_config['workspace_name']}")
    print(f"  - Environment: {loaded_config['environment']}")
    print(f"  - Config source: In-memory dictionary")
    print(f"  - Has file path: {manager.workspace_path is not None}")
    print(f"  - Is loaded: {manager.is_loaded}")

    print(f"\nFeatures:")
    print(f"  - Storage mode: {loaded_config['storage']['mode']}")
    print(f"  - Excel enabled: {loaded_config['excel']['enabled']}")
    print(f"  - Database enabled: {loaded_config['database']['enabled']}")

    print(f"\nUse Cases for Dictionary Loading:")
    print(f"  - Unit testing (no file system dependency)")
    print(f"  - Dynamic config generation from templates")
    print(f"  - Loading from databases or external APIs")
    print(f"  - Temporary workspaces for one-time operations")

    return loaded_config


if __name__ == "__main__":
    print("="*60)
    print("MediaPlanPy v3.0 - Workspace Loading Examples")
    print("="*60)

    print("\n=== Example 1: Load by Path ===")
    config1 = load_by_path()

    print("\n=== Example 2: Load by Workspace ID ===")
    config2 = load_by_workspace_id()

    print("\n=== Example 3: Load by Dictionary ===")
    config3 = load_by_dict()

    print("\n" + "="*60)
    print("Workspace Loading Examples Completed!")
    print("="*60)
    print(f"\nLoaded workspaces using different methods:")
    if config1:
        print(f"  1. By path: {config1['workspace_name']}")
    else:
        print(f"  1. By path: (skipped - configuration required)")
    if config2:
        print(f"  2. By ID: {config2['workspace_name']}")
    else:
        print(f"  2. By ID: (skipped - configuration required)")
    print(f"  3. By dict: {config3['workspace_name']}")
    print(f"\nNext Steps:")
    print(f"  - Run examples_create_mediaplan.py to create media plans")
    print(f"  - Use these loaded workspaces for media plan storage")
