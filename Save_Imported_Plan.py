"""
Import from Excel and Save to Workspace
========================================
Calls the existing import_excel_from_workspace() function from
examples_07_import_mediaplan.py, then saves the result to workspace
storage (JSON + Parquet).

How to Run (Windows):
    python import_and_save.py

Prerequisites:
    - Workspace ID set below
    - Excel file already placed in your workspace /imports/ or root folder
"""

import sys
import os

# ============================================================================
# CONFIGURATION
# ============================================================================

WORKSPACE_ID = "workspace_b92ee88b"

# ============================================================================

# Make the examples folder importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "examples"))

from examples_07_import_mediaplan import import_excel_from_workspace
from mediaplanpy.workspace import WorkspaceManager


def main():
    # Load workspace
    print(f"Loading workspace: {WORKSPACE_ID}")
    manager = WorkspaceManager()
    manager.load(workspace_id=WORKSPACE_ID)
    print("  ✓ Workspace loaded\n")

    # Run Example 3 import (prompts you for the Excel filename)
    imported_plan = import_excel_from_workspace(manager)

    if imported_plan is None:
        print("\nNo plan was imported. Exiting.")
        return

    # Save — writes JSON + Parquet to workspace storage
    print(f"\nSaving imported plan to workspace...")
    saved_path = imported_plan.save(manager)
    print(f"  ✓ Saved: {saved_path}")
    print(f"\n  Plan ID:   {imported_plan.meta.id}")
    print(f"  Plan Name: {imported_plan.meta.name}")


if __name__ == "__main__":
    main()