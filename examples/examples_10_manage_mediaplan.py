"""
MediaPlanPy Examples - Manage Media Plan

This script demonstrates media plan lifecycle management using MediaPlanPy SDK v3.0.
Shows delete, archive, restore, and version management operations.

v3.0 Features Demonstrated:
- delete() with dry_run preview
- archive() to mark plans as inactive
- restore() to reactivate archived plans
- set_as_current() for version management
- is_archived and is_current meta fields
- parent_id for version lineage tracking
- Version management workflows

Prerequisites:
- MediaPlanPy SDK v3.0.0+ installed
- Workspace created (see examples_create_workspace.py)
- Media plans created (see examples_create_mediaplan.py)

How to Run:
1. First run examples_create_workspace.py to create a workspace
2. Then run examples_create_mediaplan.py to create media plans
3. Update WORKSPACE_ID below, or provide when prompted
4. Open this file in your IDE
5. Run the entire script: python examples_manage_mediaplan.py

Next Steps After Running:
- Use lifecycle methods in production workflows
- Implement version control strategies
- Build approval workflows with version management
- Clean up old archived plans periodically
"""

from mediaplanpy.workspace import WorkspaceManager
from mediaplanpy.models import MediaPlan


# ============================================================================
# USER CONFIGURATION
# Update these values after creating workspace and media plans
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
    print(f"  2. Type 'skip' to skip")
    print(f"  3. Update the constant at the top of this file and re-run")

    user_input = input(f"\n{prompt_message}: ").strip()

    if user_input.lower() == 'skip':
        print("Skipping.")
        return None

    if user_input:
        return user_input
    else:
        print("No value provided. Skipping.")
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


def create_test_plan(manager):
    """
    Create a simple test plan for management examples.

    Args:
        manager: Loaded WorkspaceManager instance

    Returns:
        MediaPlan instance
    """
    print("\nCreating test media plan...")

    plan = MediaPlan.create(
        campaign_name="Management Test Campaign",
        campaign_objective="Test management operations",
        campaign_budget_total=10000.00,
        campaign_start_date="2025-01-01",
        campaign_end_date="2025-03-31",
        created_by_name="examples_user"
    )

    # Add a line item
    plan.create_lineitem({
        "name": "Test Line Item",
        "cost_total": 10000.00
    })

    # Save the plan
    plan.save(manager)

    print(f"✓ Created test plan: {plan.meta.id}")
    print(f"  - Name: {plan.meta.name}")
    print(f"  - Campaign: {plan.campaign.name}")

    return plan


def delete_mediaplan(manager):
    """
    Demonstrate deleting a media plan with dry_run preview.

    Use Case:
        When you need to permanently remove media plans from storage,
        with option to preview before deletion.

    v3.0 Features:
        - delete() method with dry_run option
        - Preview files that will be deleted
        - Removes JSON and Parquet files
        - Removes database records if configured
        - Returns detailed deletion report

    Args:
        manager: Loaded WorkspaceManager instance

    Next Steps:
        - Use dry_run=True to preview before deletion
        - Verify plan is no longer loadable after deletion
        - Clean up old/obsolete plans periodically
    """
    print("\n" + "="*60)
    print("Example 1: Delete Media Plan")
    print("="*60)

    # Create a test plan to delete
    plan = create_test_plan(manager)
    plan_id = plan.meta.id

    # ====================
    # STEP 1: Dry run - preview what will be deleted
    # ====================
    print(f"\n" + "-"*60)
    print("Step 1: Preview Deletion (dry_run=True)")
    print("-"*60)

    print(f"\nRunning dry_run to preview deletion...")

    result = plan.delete(workspace_manager=manager, dry_run=True)

    print(f"\n✓ Dry run completed")
    print(f"\nPreview - would delete:")
    print(f"  - Plan ID: {result['mediaplan_id']}")
    print(f"  - Schema version: {result['schema_version']}")
    print(f"  - Files found: {result['files_found']}")

    if result['deleted_files']:
        print(f"\nFiles that would be deleted:")
        for file_path in result['deleted_files']:
            print(f"    • {file_path}")

    if result['errors']:
        print(f"\nWarnings:")
        for error in result['errors']:
            print(f"    • {error}")

    # ====================
    # STEP 2: Actual deletion
    # ====================
    print(f"\n" + "-"*60)
    print("Step 2: Actual Deletion (dry_run=False)")
    print("-"*60)

    print(f"\nDeleting media plan permanently...")

    result = plan.delete(workspace_manager=manager, dry_run=False)

    print(f"\n✓ Deletion completed")
    print(f"  - Files found: {result['files_found']}")
    print(f"  - Files deleted: {result['files_deleted']}")

    if result['deleted_files']:
        print(f"\nDeleted files:")
        for file_path in result['deleted_files']:
            print(f"    • {file_path}")

    if result['database_deleted']:
        print(f"\nDatabase:")
        print(f"    • Rows deleted: {result['database_rows_deleted']}")

    # ====================
    # STEP 3: Verify deletion
    # ====================
    print(f"\n" + "-"*60)
    print("Step 3: Verify Deletion")
    print("-"*60)

    print(f"\nAttempting to load deleted plan...")

    try:
        MediaPlan.load(manager, media_plan_id=plan_id)
        print(f"⚠ Plan still exists (unexpected)")
    except Exception as e:
        print(f"✓ Plan no longer exists (expected)")
        print(f"  - Error: {type(e).__name__}")

    print(f"\n✓ Successfully demonstrated delete with dry_run preview")


def archive_and_restore_mediaplan(manager):
    """
    Demonstrate archiving and restoring media plans.

    Use Case:
        When you want to mark plans as inactive without deleting them.
        Archived plans are kept in storage but marked with is_archived=True.

    v3.0 Features:
        - archive() sets is_archived=True
        - restore() sets is_archived=False
        - Archived plans can still be loaded
        - Query filters can include/exclude archived plans
        - Maintains full plan data and history

    Args:
        manager: Loaded WorkspaceManager instance

    Next Steps:
        - Use archive() for inactive/completed plans
        - Use restore() to reactivate archived plans
        - Query with filters to show/hide archived plans
        - Implement archival policies (e.g., archive after 90 days)
    """
    print("\n" + "="*60)
    print("Example 2: Archive and Restore Media Plan")
    print("="*60)

    # Create a test plan to archive
    plan = create_test_plan(manager)
    plan_id = plan.meta.id

    # ====================
    # STEP 1: Archive the plan
    # ====================
    print(f"\n" + "-"*60)
    print("Step 1: Archive Media Plan")
    print("-"*60)

    print(f"\nBefore archiving:")
    print(f"  - is_archived: {plan.meta.is_archived}")

    print(f"\nArchiving media plan...")

    plan.archive(workspace_manager=manager)

    print(f"\n✓ Plan archived successfully")
    print(f"  - is_archived: {plan.meta.is_archived}")

    # ====================
    # STEP 2: Verify archived plans are excluded from queries by default
    # ====================
    print(f"\n" + "-"*60)
    print("Step 2: Query Behavior with Archived Plans")
    print("-"*60)

    print(f"\nQuerying all non-archived plans...")

    query = """
    SELECT DISTINCT meta_id, meta_name, meta_is_archived
    FROM {*}
    WHERE meta_is_archived = FALSE OR meta_is_archived IS NULL
    ORDER BY meta_name
    """

    df = manager.sql_query(query, return_dataframe=True)

    print(f"✓ Found {len(df)} non-archived plans")

    # Check if our archived plan is in the results
    archived_plan_in_results = plan_id in df['meta_id'].values if len(df) > 0 else False

    if archived_plan_in_results:
        print(f"⚠ Archived plan appears in non-archived query (unexpected)")
    else:
        print(f"✓ Archived plan correctly excluded from non-archived query")

    print(f"\nQuerying all plans (including archived)...")

    query_all = """
    SELECT DISTINCT meta_id, meta_name, meta_is_archived
    FROM {*}
    ORDER BY meta_name
    """

    df_all = manager.sql_query(query_all, return_dataframe=True)

    print(f"✓ Found {len(df_all)} total plans (including archived)")

    # ====================
    # STEP 3: Restore the archived plan
    # ====================
    print(f"\n" + "-"*60)
    print("Step 3: Restore Archived Plan")
    print("-"*60)

    print(f"\nRestoring media plan...")

    plan.restore(workspace_manager=manager)

    print(f"\n✓ Plan restored successfully")
    print(f"  - is_archived: {plan.meta.is_archived}")

    # ====================
    # STEP 4: Verify restored plan appears in queries
    # ====================
    print(f"\n" + "-"*60)
    print("Step 4: Verify Restored Plan in Queries")
    print("-"*60)

    print(f"\nQuerying non-archived plans again...")

    df_after_restore = manager.sql_query(query, return_dataframe=True)

    print(f"✓ Found {len(df_after_restore)} non-archived plans")

    # Check if our restored plan is now in the results
    restored_plan_in_results = plan_id in df_after_restore['meta_id'].values if len(df_after_restore) > 0 else False

    if restored_plan_in_results:
        print(f"✓ Restored plan appears in non-archived query (expected)")
    else:
        print(f"⚠ Restored plan not in non-archived query (unexpected)")

    # Clean up - delete the test plan
    print(f"\nCleaning up test plan...")
    plan.delete(workspace_manager=manager, dry_run=False)
    print(f"✓ Test plan deleted")

    print(f"\n✓ Successfully demonstrated archive and restore operations")


def manage_plan_versions(manager):
    """
    Demonstrate version management with set_as_current().

    Use Case:
        When you need to manage multiple versions of the same campaign
        and control which version is the "current" active version.

    v3.0 Features:
        - overwrite=False creates new versions with new IDs
        - parent_id links versions together
        - is_current=True marks the active version
        - set_as_current() switches active version
        - Only one version per campaign can be current

    Args:
        manager: Loaded WorkspaceManager instance

    Next Steps:
        - Create version control workflows
        - Implement approval processes (promote to current)
        - Track version history via parent_id
        - Query specific versions or just current versions
    """
    print("\n" + "="*60)
    print("Example 3: Manage Plan Versions")
    print("="*60)

    # ====================
    # STEP 1: Create initial version
    # ====================
    print(f"\n" + "-"*60)
    print("Step 1: Create Initial Version")
    print("-"*60)

    print(f"\nCreating initial media plan version...")

    plan_v1 = MediaPlan.create(
        campaign_name="Version Control Campaign",
        campaign_objective="Demonstrate version management",
        campaign_budget_total=50000.00,
        campaign_start_date="2025-01-01",
        campaign_end_date="2025-06-30",
        created_by_name="examples_user",
        media_plan_name="plan_v1"
    )

    plan_v1.create_lineitem({
        "name": "Social Media Line Item",
        "cost_total": 20000.00
    })

    # Save as current version
    plan_v1.save(manager, set_as_current=True)

    print(f"\n✓ Created Version 1")
    print(f"  - ID: {plan_v1.meta.id}")
    print(f"  - Name: {plan_v1.meta.name}")
    print(f"  - is_current: {plan_v1.meta.is_current}")
    print(f"  - parent_id: {plan_v1.meta.parent_id}")

    # ====================
    # STEP 2: Create second version
    # ====================
    print(f"\n" + "-"*60)
    print("Step 2: Create Second Version")
    print("-"*60)

    print(f"\nModifying plan and saving as new version...")

    # Modify the plan
    plan_v1.meta.name = "plan_v2"
    plan_v1.campaign.budget_total = 60000.00
    plan_v1.create_lineitem({
        "name": "Search Line Item",
        "cost_total": 25000.00
    })

    # Save as new version (overwrite=False creates new ID, parent_id links to v1)
    plan_v1.save(manager, overwrite=False, set_as_current=True)

    plan_v2_id = plan_v1.meta.id  # ID has changed after save with overwrite=False
    parent_id = plan_v1.meta.parent_id

    print(f"\n✓ Created Version 2")
    print(f"  - ID: {plan_v2_id}")
    print(f"  - Name: {plan_v1.meta.name}")
    print(f"  - parent_id: {parent_id} (links to Version 1)")
    print(f"  - is_current: {plan_v1.meta.is_current}")
    print(f"  - Budget: ${plan_v1.campaign.budget_total:,.2f}")
    print(f"  - Line items: {len(plan_v1.lineitems)}")

    # ====================
    # STEP 3: Create third version
    # ====================
    print(f"\n" + "-"*60)
    print("Step 3: Create Third Version")
    print("-"*60)

    print(f"\nModifying plan and saving as another new version...")

    # Modify the plan
    plan_v1.meta.name = "plan_v3"
    plan_v1.campaign.budget_total = 75000.00
    plan_v1.create_lineitem({
        "name": "Display Line Item",
        "cost_total": 30000.00
    })

    # Save as new version
    plan_v1.save(manager, overwrite=False, set_as_current=True)

    plan_v3_id = plan_v1.meta.id  # ID has changed again
    parent_id_v3 = plan_v1.meta.parent_id  # Should link to v2

    print(f"\n✓ Created Version 3")
    print(f"  - ID: {plan_v3_id}")
    print(f"  - Name: {plan_v1.meta.name}")
    print(f"  - parent_id: {parent_id_v3} (links to Version 2)")
    print(f"  - is_current: {plan_v1.meta.is_current}")
    print(f"  - Budget: ${plan_v1.campaign.budget_total:,.2f}")
    print(f"  - Line items: {len(plan_v1.lineitems)}")

    # ====================
    # STEP 4: List all versions
    # ====================
    print(f"\n" + "-"*60)
    print("Step 4: List All Versions")
    print("-"*60)

    print(f"\nQuerying all versions of the campaign...")

    # Get campaign_id from current plan
    campaign_id = plan_v1.campaign.id

    query = f"""
    SELECT DISTINCT
        meta_id,
        meta_name,
        meta_parent_id,
        meta_is_current,
        meta_created_at,
        campaign_budget_total
    FROM {{*}}
    WHERE campaign_id = '{campaign_id}'
    ORDER BY meta_created_at
    """

    df = manager.sql_query(query, return_dataframe=True)

    print(f"\n✓ Found {len(df)} versions")

    if len(df) > 0:
        print(f"\nAll Versions:")
        for idx, row in df.iterrows():
            is_current_marker = " ← CURRENT" if row['meta_is_current'] else ""
            print(f"  {idx + 1}. {row['meta_name']}{is_current_marker}")
            print(f"     • ID: {row['meta_id']}")
            print(f"     • Budget: ${row['campaign_budget_total']:,.2f}")
            print(f"     • parent_id: {row['meta_parent_id']}")
            print(f"     • is_current: {row['meta_is_current']}")

    # ====================
    # STEP 5: Switch current version
    # ====================
    print(f"\n" + "-"*60)
    print("Step 5: Switch Current Version")
    print("-"*60)

    print(f"\nCurrently, Version 3 is current")
    print(f"Let's switch back to Version 1...")

    # Load Version 1
    version_1_id = parent_id  # The original version

    try:
        plan_v1_reloaded = MediaPlan.load(manager, media_plan_id=version_1_id)

        print(f"\nLoaded Version 1:")
        print(f"  - ID: {plan_v1_reloaded.meta.id}")
        print(f"  - is_current before: {plan_v1_reloaded.meta.is_current}")

        # Set as current
        result = plan_v1_reloaded.set_as_current(workspace_manager=manager)

        print(f"\n✓ Switched current version")
        print(f"  - Plan set as current: {result['plan_set_as_current']}")
        print(f"  - Plans unset as current: {result['plans_unset_as_current']}")
        print(f"  - Total affected: {result['total_affected']}")

        # Verify
        plan_v1_reloaded = MediaPlan.load(manager, media_plan_id=version_1_id)
        print(f"\nVersion 1 after set_as_current:")
        print(f"  - is_current: {plan_v1_reloaded.meta.is_current}")

    except Exception as e:
        print(f"⚠ Could not load or switch to Version 1: {e}")

    # ====================
    # STEP 6: Verify current version changed
    # ====================
    print(f"\n" + "-"*60)
    print("Step 6: Verify Current Version Changed")
    print("-"*60)

    print(f"\nQuerying to see which version is now current...")

    df_after = manager.sql_query(query, return_dataframe=True)

    if len(df_after) > 0:
        print(f"\nVersions After Switch:")
        for idx, row in df_after.iterrows():
            is_current_marker = " ← CURRENT" if row['meta_is_current'] else ""
            print(f"  {idx + 1}. {row['meta_name']}{is_current_marker}")
            print(f"     • ID: {row['meta_id']}")
            print(f"     • is_current: {row['meta_is_current']}")

    # Clean up - delete all versions
    print(f"\nCleaning up test plans...")
    try:
        for version_id in df['meta_id'].values:
            plan_to_delete = MediaPlan.load(manager, media_plan_id=version_id)
            plan_to_delete.delete(workspace_manager=manager, dry_run=False)
            print(f"✓ Deleted version: {version_id}")
    except Exception as e:
        print(f"⚠ Cleanup warning: {e}")

    print(f"\n✓ Successfully demonstrated version management")


if __name__ == "__main__":
    print("="*60)
    print("MediaPlanPy v3.0 - Manage Media Plan Examples")
    print("="*60)

    # Load workspace ONCE
    print("\nLoading workspace...")
    manager = load_workspace()

    if manager is None:
        print("\nNo workspace loaded. Exiting.")
        print("\nTo run these examples:")
        print("  1. Run examples_create_workspace.py first")
        print("  2. Update WORKSPACE_ID at top of this file")
        print("  3. Or provide value when prompted")
        exit(0)

    # Run management examples
    delete_mediaplan(manager)

    archive_and_restore_mediaplan(manager)

    manage_plan_versions(manager)

    print("\n" + "="*60)
    print("Manage Media Plan Examples Completed!")
    print("="*60)

    print(f"\nWhat We Demonstrated:")
    print(f"  1. Delete with dry_run preview")
    print(f"  2. Archive to mark plans as inactive")
    print(f"  3. Restore archived plans")
    print(f"  4. Query filtering for archived plans")
    print(f"  5. Create multiple versions (overwrite=False)")
    print(f"  6. Track version lineage with parent_id")
    print(f"  7. Manage current version with set_as_current()")
    print(f"  8. Switch between versions")

    print(f"\nNext Steps:")
    print(f"  - Implement version control workflows")
    print(f"  - Build approval processes for version promotion")
    print(f"  - Use archive() for completed campaigns")
    print(f"  - Set up archival policies (e.g., archive after 90 days)")
    print(f"  - Track version history via parent_id queries")
