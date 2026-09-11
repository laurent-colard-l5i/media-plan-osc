"""
MediaPlanPy Examples - Import Media Plan

This script demonstrates how to import media plans from JSON and Excel formats using MediaPlanPy SDK v3.0.
Shows automatic schema detection, object reconstruction, and import verification.

v3.0 Features Demonstrated:
- import_from_json() with v3.0 structure
- import_from_excel() with v3.0 columns
- Automatic schema version detection
- Array reconstruction (target_audiences, target_locations)
- Nested object reconstruction (MetricFormula, Dictionary)
- Import from workspace storage
- Import from custom file paths

Prerequisites:
- MediaPlanPy SDK v3.0.0+ installed
- openpyxl library for Excel import
- Workspace created (see examples_create_workspace.py)
- Exported files available (see examples_export_mediaplan.py)

How to Run:
1. First run examples_create_workspace.py to create a workspace
2. Then run examples_create_mediaplan.py to create media plans
3. Then run examples_export_mediaplan.py to create export files
4. Update WORKSPACE_ID below, or provide when prompted
5. Open this file in your IDE
6. Run the entire script: python examples_import_mediaplan.py
7. Follow prompts to provide file names/paths for each import

Next Steps After Running:
- Verify imported plans match original
- Save imported plans to workspace
- Query imported plans
- Use imports for data migration
"""

import os
from pathlib import Path

from mediaplanpy.workspace import WorkspaceManager
from mediaplanpy.models import MediaPlan


# ============================================================================
# USER CONFIGURATION
# Update these values after creating workspace
# ============================================================================

# Copy the "Workspace ID" from examples_create_workspace.py output
WORKSPACE_ID = "workspace_b92ee88b"

# ============================================================================


def get_configuration_value(config_name, prompt_message, example_value):
    """
    Get configuration value - either from constant or interactive user input.

    Args:
        config_name: Name of the configuration constant (e.g., 'WORKSPACE_ID')
        prompt_message: Message to show when prompting user
        example_value: Example value to show user

    Returns:
        Configuration value or None if user chooses to skip
    """
    # Get the current value from constants
    if config_name == 'WORKSPACE_ID':
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
    print(f"  1. Enter the value now")
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


def load_workspace():
    """
    Load workspace once for use across all examples.

    Returns:
        WorkspaceManager or None if config not provided

    Prerequisites:
        - Run examples_create_workspace.py first to create workspaces
        - Either update WORKSPACE_ID at top of file, or provide value when prompted
    """
    # Get workspace_id
    workspace_id = get_configuration_value(
        'WORKSPACE_ID',
        'Enter workspace ID',
        'workspace_abc12345'
    )

    if workspace_id is None:
        return None

    print(f"\nLoading workspace: {workspace_id}")
    manager = WorkspaceManager()
    manager.load(workspace_id=workspace_id)
    print(f"✓ Workspace loaded successfully")

    return manager


def prompt_for_input(prompt_message, example_value, allow_skip=True):
    """
    Prompt user for input with example and skip option.

    Args:
        prompt_message: Message to show when prompting
        example_value: Example value to show
        allow_skip: Whether to allow skipping

    Returns:
        User input or None if skipped
    """
    print(f"\n{prompt_message}")
    print(f"Example: {example_value}")

    if allow_skip:
        print(f"(Type 'skip' to skip this example)")

    user_input = input(f"\nEnter value: ").strip()

    if allow_skip and user_input.lower() == 'skip':
        print("Skipping this example.")
        return None

    if user_input:
        return user_input
    else:
        print("No value provided. Skipping this example.")
        return None


def verify_imported_plan(plan, source_description):
    """
    Verify that a plan was imported successfully by showing basic info.

    Args:
        plan: The imported MediaPlan instance
        source_description: Description of import source (e.g., "workspace JSON file")
    """
    print(f"\n" + "-"*60)
    print("Verifying Import")
    print("-"*60)

    print(f"\n✓ Successfully imported from {source_description}")

    print(f"\nMedia Plan:")
    print(f"  - ID: {plan.meta.id}")
    print(f"  - Name: {plan.meta.name}")
    print(f"  - Schema version: {plan.meta.schema_version}")

    print(f"\nCampaign:")
    print(f"  - Name: {plan.campaign.name}")
    print(f"  - Budget: ${plan.campaign.budget_total:,.2f}")

    # Check for v3.0 features
    if plan.campaign.target_audiences:
        print(f"  - Target audiences: {len(plan.campaign.target_audiences)}")

    if plan.campaign.target_locations:
        print(f"  - Target locations: {len(plan.campaign.target_locations)}")

    print(f"\nLine Items:")
    print(f"  - Count: {len(plan.lineitems)}")


def import_json_from_workspace(manager):
    """
    Import media plan from JSON file in workspace storage.

    Use Case:
        When you need to import JSON files that were exported to workspace
        storage (in the /exports/ directory).

    v3.0 Features:
        - Automatic schema version detection (v3.0)
        - Array reconstruction (target_audiences, target_locations)
        - Nested object reconstruction (MetricFormula, Dictionary)
        - Import from workspace /imports/ or root directory

    Args:
        manager: Loaded WorkspaceManager instance

    Returns:
        Imported MediaPlan instance or None if skipped

    Next Steps:
        - Save imported plan to workspace if needed
        - Verify imported data
        - Use for data synchronization
    """
    print("\n" + "="*60)
    print("Example 1: Import JSON from Workspace Storage")
    print("="*60)

    print("\nThis will import a JSON file from your workspace storage.")
    print("The file should be in the /imports/ or root directory.")

    # Prompt for file name
    file_name = prompt_for_input(
        "Enter JSON file name to import from workspace",
        "mediaplan_abc12345.json"
    )

    if file_name is None:
        return None

    print(f"\nImporting: {file_name}")
    print(f"From: Workspace storage")

    try:
        # Import from workspace storage
        # The method will look in /imports/ directory first, then root
        imported_plan = MediaPlan.import_from_json(
            file_name=file_name,
            workspace_manager=manager
        )

        verify_imported_plan(imported_plan, "workspace JSON file")

        return imported_plan

    except Exception as e:
        print(f"\n⚠ Import failed: {e}")
        print(f"\nTroubleshooting:")
        print(f"  - Ensure the file exists in workspace /imports/ or root directory")
        print(f"  - Check the file name is correct")
        print(f"  - Verify the file is valid JSON")
        return None


def import_json_from_path():
    """
    Import media plan from JSON file at custom file path.

    Use Case:
        When you need to import JSON files from custom locations outside
        of workspace storage (e.g., downloaded files, external sources).

    v3.0 Features:
        - Automatic schema version detection
        - Complete v3.0 structure reconstruction
        - Works with any file system location

    Returns:
        Imported MediaPlan instance or None if skipped

    Next Steps:
        - Save imported plan to workspace
        - Use for data migration from external sources
    """
    print("\n" + "="*60)
    print("Example 2: Import JSON from Custom Path")
    print("="*60)

    print("\nThis will import a JSON file from a custom file path.")
    print("Provide the full path to the JSON file.")

    # Prompt for full path
    file_path = prompt_for_input(
        "Enter full path to JSON file",
        "C:/mediaplanpy/exports/mediaplan_abc12345.json"
    )

    if file_path is None:
        return None

    # Check if file exists
    if not os.path.exists(file_path):
        print(f"\n⚠ File not found: {file_path}")
        return None

    print(f"\nImporting: {file_path}")

    try:
        # Import from custom file path
        imported_plan = MediaPlan.import_from_json(
            file_name=os.path.basename(file_path),
            file_path=os.path.dirname(file_path)  # Directory only
        )

        verify_imported_plan(imported_plan, "custom JSON file path")

        return imported_plan

    except Exception as e:
        print(f"\n⚠ Import failed: {e}")
        print(f"\nTroubleshooting:")
        print(f"  - Verify the file exists at the specified path")
        print(f"  - Check the file is valid JSON")
        print(f"  - Ensure the file contains a valid media plan")
        return None


def import_excel_from_workspace(manager):
    """
    Import media plan from Excel file in workspace storage.

    Use Case:
        When you need to import Excel files that were exported to workspace
        storage or created from templates.

    v3.0 Features:
        - Automatic schema version detection
        - v3.0 column parsing
        - Array reconstruction from Excel data
        - Import from workspace /imports/ or root directory

    Args:
        manager: Loaded WorkspaceManager instance

    Returns:
        Imported MediaPlan instance or None if skipped

    Next Steps:
        - Save imported plan to workspace if needed
        - Use for bulk data entry workflows
    """
    print("\n" + "="*60)
    print("Example 3: Import Excel from Workspace Storage")
    print("="*60)

    print("\nThis will import an Excel file from your workspace storage.")
    print("The file should be in the /imports/ or root directory.")

    # Prompt for file name
    file_name = prompt_for_input(
        "Enter Excel file name to import from workspace",
        "mediaplan_abc12345.xlsx"
    )

    if file_name is None:
        return None

    print(f"\nImporting: {file_name}")
    print(f"From: Workspace storage")

    try:
        # Import from workspace storage
        imported_plan = MediaPlan.import_from_excel(
            file_name=file_name,
            workspace_manager=manager
        )

        verify_imported_plan(imported_plan, "workspace Excel file")

        return imported_plan

    except ImportError:
        print(f"\n⚠ Excel import requires openpyxl library")
        print(f"  Install with: pip install openpyxl")
        return None
    except Exception as e:
        print(f"\n⚠ Import failed: {e}")
        print(f"\nTroubleshooting:")
        print(f"  - Ensure the file exists in workspace /imports/ or root directory")
        print(f"  - Check the file name is correct")
        print(f"  - Verify the file is valid Excel (.xlsx)")
        print(f"  - Ensure openpyxl is installed: pip install openpyxl")
        return None


def import_excel_from_path():
    """
    Import media plan from Excel file at custom file path.

    Use Case:
        When you need to import Excel files from custom locations outside
        of workspace storage (e.g., downloads, shared drives, templates).

    v3.0 Features:
        - Automatic schema version detection
        - v3.0 column parsing
        - Array reconstruction from Excel
        - Works with any file system location

    Returns:
        Imported MediaPlan instance or None if skipped

    Next Steps:
        - Save imported plan to workspace
        - Use for manual data entry workflows
        - Import from external systems
    """
    print("\n" + "="*60)
    print("Example 4: Import Excel from Custom Path")
    print("="*60)

    print("\nThis will import an Excel file from a custom file path.")
    print("Provide the full path to the Excel file.")

    # Prompt for full path
    file_path = prompt_for_input(
        "Enter full path to Excel file",
        "C:/mediaplanpy/exports/mediaplan_abc12345.xlsx"
    )

    if file_path is None:
        return None

    # Check if file exists
    if not os.path.exists(file_path):
        print(f"\n⚠ File not found: {file_path}")
        return None

    print(f"\nImporting: {file_path}")

    try:
        # Import from custom file path
        imported_plan = MediaPlan.import_from_excel(
            file_name=os.path.basename(file_path),
            file_path=os.path.dirname(file_path)  # Directory only
        )

        verify_imported_plan(imported_plan, "custom Excel file path")

        return imported_plan

    except ImportError:
        print(f"\n⚠ Excel import requires openpyxl library")
        print(f"  Install with: pip install openpyxl")
        return None
    except Exception as e:
        print(f"\n⚠ Import failed: {e}")
        print(f"\nTroubleshooting:")
        print(f"  - Verify the file exists at the specified path")
        print(f"  - Check the file is valid Excel (.xlsx)")
        print(f"  - Ensure openpyxl is installed: pip install openpyxl")
        return None


if __name__ == "__main__":
    print("="*60)
    print("MediaPlanPy v3.0 - Import Media Plan Examples")
    print("="*60)

    # Load workspace ONCE
    print("\nLoading workspace...")
    manager = load_workspace()

    if manager is None:
        print("\nNo workspace loaded. Exiting.")
        print("\nTo run these examples:")
        print("  1. Run examples_create_workspace.py first")
        print("  2. Run examples_create_mediaplan.py to create plans")
        print("  3. Run examples_export_mediaplan.py to create export files")
        print("  4. Update WORKSPACE_ID at top of this file")
        print("  5. Or provide value when prompted")
        exit(0)

    # Run import examples - each prompts for input just before importing
    print("\n" + "="*60)
    print("Import Examples")
    print("="*60)
    print("\nYou will be prompted for file names/paths before each import.")
    print("Type 'skip' at any prompt to skip that example.")

    plan1 = import_json_from_workspace(manager)

    plan2 = import_json_from_path()

    plan3 = import_excel_from_workspace(manager)

    plan4 = import_excel_from_path()

    print("\n" + "="*60)
    print("Import Media Plan Examples Completed!")
    print("="*60)

    # Summary
    imported_count = sum(1 for p in [plan1, plan2, plan3, plan4] if p is not None)

    print(f"\nSuccessfully imported: {imported_count} / 4 examples")

    print(f"\nWhat We Demonstrated:")
    print(f"  1. Imported JSON from workspace storage")
    print(f"  2. Imported JSON from custom file path")
    print(f"  3. Imported Excel from workspace storage")
    print(f"  4. Imported Excel from custom file path")
    print(f"  5. Automatic schema version detection")
    print(f"  6. Array reconstruction (target_audiences, target_locations)")
    print(f"  7. Nested object reconstruction (MetricFormula, Dictionary)")

    print(f"\nNext Steps:")
    print(f"  - Save imported plans to workspace: plan.save(manager)")
    print(f"  - Query imported plans: manager.list_mediaplans()")
    print(f"  - Use for data migration workflows")
    print(f"  - Compare imported vs original plans")
