"""
Import from Excel and Save / Load Existing Plan and Save
=========================================================
Offers two workflows:

  Option 1 — Import from Excel (new or updated plan)
      Calls import_excel_from_workspace() from examples_07_import_mediaplan.py,
      then saves to workspace storage (JSON + Parquet + database if enabled).

  Option 2 — Load existing plan by ID and save
      Loads a plan already in workspace storage by its media plan ID,
      then re-saves it. Use this to sync pre-existing plans to the database
      after enabling the PostgreSQL integration.

How to Run (Windows):
    python import_and_save.py

Prerequisites:
    - Workspace ID set below
    - For Option 1: Excel file placed in your workspace /imports/ or root folder
    - For Option 2: Media plan already saved in workspace storage
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
from mediaplanpy.models import MediaPlan


def prompt_choice(prompt, valid_options):
    """Prompt the user until they enter a valid option."""
    while True:
        value = input(prompt).strip()
        if value in valid_options:
            return value
        print(f"  Please enter one of: {', '.join(valid_options)}")


def option1_import_from_excel(manager):
    """Import a plan from an Excel file and save to workspace."""
    plan = import_excel_from_workspace(manager)

    if plan is None:
        print("\nNo plan was imported. Exiting.")
        return

    print(f"\nSaving imported plan to workspace...")
    saved_path = plan.save(manager)
    print(f"  ✓ Saved: {saved_path}")
    print(f"\n  Plan ID:   {plan.meta.id}")
    print(f"  Plan Name: {plan.meta.name}")


def option2_load_and_save(manager):
    """Load an existing plan by ID and re-save it (syncs to database)."""
    print("\n" + "="*60)
    print("Option 2: Load Existing Plan by ID and Save")
    print("="*60)
    print("\nEnter the media plan ID to load (e.g. mediaplan_xxxxxxxx).")
    print("Type 'skip' to cancel.\n")

    media_plan_id = input("Media Plan ID: ").strip()

    if media_plan_id.lower() == "skip" or not media_plan_id:
        print("Cancelled.")
        return

    print(f"\nLoading plan: {media_plan_id}")
    try:
        plan = MediaPlan.load(workspace_manager=manager, media_plan_id=media_plan_id)
        print(f"  ✓ Loaded: {plan.meta.name}")
    except Exception as e:
        print(f"\n  ✗ Could not load plan: {e}")
        return

    print(f"\nSaving plan to workspace (including database sync)...")
    try:
        saved_path = plan.save(manager)
        print(f"  ✓ Saved: {saved_path}")
        print(f"\n  Plan ID:   {plan.meta.id}")
        print(f"  Plan Name: {plan.meta.name}")
    except Exception as e:
        print(f"\n  ✗ Save failed: {e}")


def main():
    # Load workspace
    print(f"Loading workspace: {WORKSPACE_ID}")
    manager = WorkspaceManager()
    manager.load(workspace_id=WORKSPACE_ID)
    print("  ✓ Workspace loaded\n")

    # Prompt for workflow choice
    print("What would you like to do?")
    print("  1 — Import from Excel (new plan)")
    print("  2 — Load existing plan by ID (e.g. to sync to database)")
    print("  q — Quit\n")

    choice = prompt_choice("Enter choice (1, 2, or q): ", ["1", "2", "q"])

    if choice == "q":
        print("Exiting.")
        return
    elif choice == "1":
        option1_import_from_excel(manager)
    elif choice == "2":
        option2_load_and_save(manager)


if __name__ == "__main__":
    main()
