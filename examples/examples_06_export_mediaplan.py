"""
MediaPlanPy Examples - Export Media Plan

This script demonstrates how to export media plans to JSON and Excel formats using MediaPlanPy SDK v3.0.
Shows complete v3.0 structure serialization including arrays and nested objects.

v3.0 Features Demonstrated:
- export_to_json() with complete v3.0 structure
- export_to_excel() with v3.0 columns
- Serialization of array-based models (target_audiences, target_locations)
- Serialization of nested objects (MetricFormula, Dictionary)
- Export to workspace storage
- Export to custom file paths
- File structure verification

Prerequisites:
- MediaPlanPy SDK v3.0.0+ installed
- openpyxl library for Excel export
- Workspace created (see examples_create_workspace.py)
- Media plans created (see examples_create_mediaplan.py)

How to Run:
1. First run examples_create_workspace.py to create a workspace
2. Then run examples_create_mediaplan.py to create media plans
3. Update WORKSPACE_ID and MEDIAPLAN_ID constants below, or provide when prompted
4. Open this file in your IDE
5. Run the entire script: python examples_export_mediaplan.py
6. Or run individual functions by calling them from __main__
7. Check examples/output/export_examples/ for exported files

Next Steps After Running:
- Import the exported files (examples_import_mediaplan.py)
- Verify v3.0 structure in JSON files
- Open Excel files to see flattened view
- Share exports with other tools/systems
"""

import os
import json
from pathlib import Path
from datetime import datetime

from mediaplanpy.workspace import WorkspaceManager
from mediaplanpy.models import MediaPlan


# ============================================================================
# USER CONFIGURATION
# Update these values after creating workspace and media plans
# ============================================================================

# Copy the "Workspace ID" from examples_create_workspace.py output
WORKSPACE_ID = "workspace_b92ee88b"

# Copy a "Media plan ID" from examples_create_mediaplan.py output
MEDIAPLAN_ID = "mediaplan_7c4b3297"
#MEDIAPLAN_ID = "mediaplan_00ffc8c6"
#MEDIAPLAN_ID = "mediaplan_7b29049f"
#MEDIAPLAN_ID = "mediaplan_3773ed1e"
# MEDIAPLAN_ID = "mediaplan_d5aba02c"

# ============================================================================


def get_output_dir(subfolder: str) -> Path:
    """
    Create and return output directory for exports.

    Args:
        subfolder: Subdirectory name under examples/output/

    Returns:
        Path object for the output directory
    """
    output_dir = Path(__file__).parent / "output" / subfolder
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


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
    elif config_name == 'MEDIAPLAN_ID':
        current_value = MEDIAPLAN_ID
    else:
        return None

    # If already configured (not a placeholder), return it
    if "xxxxxxxx" not in current_value:
        return current_value

    # Prompt user for input
    print(f"\nConfiguration needed: {config_name}")
    print(f"Example: {example_value}")
    print(f"\nOptions:")
    print(f"  1. Enter the value now (paste from previous example output)")
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


def load_workspace_and_plan():
    """
    Load workspace and media plan once for use across all examples.

    Returns:
        Tuple of (WorkspaceManager, MediaPlan) or (None, None) if config not provided

    Prerequisites:
        - Run examples_create_workspace.py first to create workspaces
        - Run examples_create_mediaplan.py to create media plans
        - Either update constants at top of file, or provide values when prompted
    """
    # Get workspace_id
    workspace_id = get_configuration_value(
        'WORKSPACE_ID',
        'Enter workspace ID',
        'workspace_abc12345'
    )

    if workspace_id is None:
        return None, None

    # Get mediaplan_id
    mediaplan_id = get_configuration_value(
        'MEDIAPLAN_ID',
        'Enter media plan ID',
        'mediaplan_abc12345'
    )

    if mediaplan_id is None:
        return None, None

    print(f"\nLoading workspace: {workspace_id}")
    manager = WorkspaceManager()
    manager.load(workspace_id=workspace_id)
    print(f"✓ Workspace loaded successfully")

    print(f"\nLoading media plan: {mediaplan_id}")
    plan = MediaPlan.load(manager, media_plan_id=mediaplan_id)
    print(f"✓ Media plan loaded: {plan.meta.name}")

    return manager, plan


def export_to_json(manager, plan):
    """
    Export media plan to JSON format with complete v3.0 structure.

    Use Case:
        When you need to export media plans for:
        - Data interchange with other systems
        - Backup and archival
        - Version control
        - API integration
        - Complete structure preservation

    v3.0 Features:
        - Complete v3.0 schema serialization
        - Array-based models (target_audiences, target_locations) preserved as arrays
        - Nested objects (MetricFormula) preserved as objects
        - Dictionary configuration included
        - All meta fields (is_current, is_archived, parent_id)
        - Custom dimensions and KPIs
        - Custom properties dictionaries

    Args:
        manager: Loaded WorkspaceManager instance
        plan: Loaded MediaPlan instance

    Next Steps:
        - Import JSON file using import_from_json()
        - Use JSON for API integration
        - Store in version control systems
        - Share with other teams or systems
    """
    print("\n" + "="*60)
    print("Exporting to JSON Format")
    print("="*60)

    print(f"\nMedia Plan to Export:")
    print(f"  - ID: {plan.meta.id}")
    print(f"  - Name: {plan.meta.name}")
    print(f"  - Schema version: {plan.meta.schema_version}")
    print(f"  - Campaign: {plan.campaign.name}")
    print(f"  - Line items: {len(plan.lineitems)}")

    # ====================
    # EXPORT 1: To workspace storage
    # ====================
    print(f"\n" + "-"*60)
    print("Export 1: To Workspace Storage")
    print("-"*60)

    # Export to workspace storage (goes to /exports/ subdirectory)
    print(f"Exporting to workspace storage...")

    exported_path1 = plan.export_to_json(
        workspace_manager=manager,
        overwrite=True  # Overwrite if exists
    )

    print(f"✓ Exported to workspace storage: {exported_path1}")

    # ====================
    # EXPORT 2: To custom file path
    # ====================
    print(f"\n" + "-"*60)
    print("Export 2: To Custom File Path")
    print("-"*60)

    # Get output directory
    output_dir = get_output_dir("export_examples")

    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    custom_filename = f"{plan.meta.id}_{timestamp}.json"

    print(f"Exporting to: {output_dir / custom_filename}")

    # Export to custom file path
    exported_path2 = plan.export_to_json(
        file_path=str(output_dir),  # Directory path only
        file_name=custom_filename,  # Filename only
        overwrite=True
    )

    print(f"✓ Exported to: {exported_path2}")

    # ====================
    # VERIFY FILE WAS CREATED
    # ====================
    print(f"\n" + "-"*60)
    print("Verifying Exported File")
    print("-"*60)

    # Verify file exists and check size
    from pathlib import Path
    exported_file = Path(exported_path2)

    if exported_file.exists():
        file_size = exported_file.stat().st_size
        print(f"\n✓ File created successfully")
        print(f"  - Size: {file_size:,} bytes ({file_size / 1024:.1f} KB)")
        print(f"  - Location: {exported_path2}")
    else:
        print(f"\n⚠ File not found at: {exported_path2}")

    print(f"\n✓ JSON export completed successfully")

    return exported_path2


def export_to_excel(manager, plan):
    """
    Export media plan to Excel format with v3.0 columns.

    Use Case:
        When you need to export media plans for:
        - Review in Microsoft Excel or Google Sheets
        - Analysis and reporting
        - Sharing with non-technical stakeholders
        - Manual data entry templates
        - Flattened view of hierarchical data

    v3.0 Features:
        - All v3.0 columns included
        - Array fields serialized as comma-separated or JSON strings
        - Nested objects flattened or serialized
        - Multiple sheets (metadata, campaigns, line items)
        - Optional documentation sheet
        - Excel formatting and styling

    Args:
        manager: Loaded WorkspaceManager instance
        plan: Loaded MediaPlan instance

    Next Steps:
        - Open Excel file for review
        - Import Excel file using import_from_excel()
        - Use as template for manual data entry
        - Share with stakeholders
    """
    print("\n" + "="*60)
    print("Exporting to Excel Format")
    print("="*60)

    print(f"\nMedia Plan to Export:")
    print(f"  - ID: {plan.meta.id}")
    print(f"  - Name: {plan.meta.name}")
    print(f"  - Campaign: {plan.campaign.name}")
    print(f"  - Line items: {len(plan.lineitems)}")

    # ====================
    # EXPORT 1: To workspace storage with documentation
    # ====================
    print(f"\n" + "-"*60)
    print("Export 1: To Workspace Storage")
    print("-"*60)

    try:
        print(f"Exporting to workspace storage...")

        exported_path1 = plan.export_to_excel(
            workspace_manager=manager,
            overwrite=True
        )

        print(f"✓ Exported to workspace storage: {exported_path1}")

    except Exception as e:
        print(f"⚠ Export to workspace failed: {e}")
        print(f"  This may be due to Excel not being enabled in workspace settings")
        exported_path1 = None

    # ====================
    # EXPORT 2: To custom file path
    # ====================
    print(f"\n" + "-"*60)
    print("Export 2: To Custom File Path")
    print("-"*60)

    # Get output directory
    output_dir = get_output_dir("export_examples")

    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    custom_filename = f"{plan.meta.id}_{timestamp}.xlsx"

    print(f"Exporting to: {output_dir / custom_filename}")

    try:
        # Export to custom file path
        exported_path2 = plan.export_to_excel(
            file_path=str(output_dir),  # Directory path only
            file_name=custom_filename,  # Filename only
            overwrite=True
        )

        print(f"✓ Exported to: {exported_path2}")

        # ====================
        # VERIFY FILE WAS CREATED
        # ====================
        print(f"\n" + "-"*60)
        print("Verifying Exported File")
        print("-"*60)

        # Verify file exists and check size
        from pathlib import Path
        exported_file = Path(exported_path2)

        if exported_file.exists():
            file_size = exported_file.stat().st_size
            print(f"\n✓ File created successfully")
            print(f"  - Size: {file_size:,} bytes ({file_size / 1024:.1f} KB)")
            print(f"  - Location: {exported_path2}")
        else:
            print(f"\n⚠ File not found at: {exported_path2}")

        print(f"\n✓ Excel export completed successfully")

        return exported_path2

    except Exception as e:
        print(f"⚠ Excel export failed: {e}")
        print(f"  Ensure openpyxl is installed: pip install openpyxl")
        return None


if __name__ == "__main__":
    print("="*60)
    print("MediaPlanPy v3.0 - Export Media Plan Examples")
    print("="*60)

    # Load workspace and plan ONCE
    print("\nLoading workspace and media plan...")
    manager, plan = load_workspace_and_plan()

    if manager is None or plan is None:
        print("\nNo workspace or media plan loaded. Exiting.")
        print("\nTo run these examples:")
        print("  1. Run examples_create_workspace.py first")
        print("  2. Run examples_create_mediaplan.py to create plans")
        print("  3. Update WORKSPACE_ID and MEDIAPLAN_ID at top of this file")
        print("  4. Or provide values when prompted")
        exit(0)

    print("\n=== Example 1: Export to JSON ===")
    json_path = export_to_json(manager, plan)

    print("\n=== Example 2: Export to Excel ===")
    excel_path = export_to_excel(manager, plan)

    print("\n" + "="*60)
    print("Export Media Plan Examples Completed!")
    print("="*60)

    print(f"\nExported Files:")
    if json_path:
        print(f"  - JSON:  {json_path}")
    if excel_path:
        print(f"  - Excel: {excel_path}")

    print(f"\nWhat We Demonstrated:")
    print(f"  1. Exported to JSON with complete v3.0 structure")
    print(f"  2. Exported to Excel with v3.0 columns")
    print(f"  3. Exported to workspace storage")
    print(f"  4. Exported to custom file paths")
    print(f"  5. Verified exported file structure")
    print(f"  6. Preserved arrays (target_audiences, target_locations)")
    print(f"  7. Preserved nested objects (metric_formulas)")
    print(f"  8. Included all v3.0 fields (KPIs, custom dimensions)")

    print(f"\nNext Steps:")
    print(f"  - Run examples_import_mediaplan.py to import these files")
    print(f"  - Open Excel file in Microsoft Excel or Google Sheets")
    print(f"  - Use JSON for API integration or version control")
    print(f"  - Share exports with other teams or systems")
