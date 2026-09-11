"""
MediaPlanPy Examples - Manage Line Items

This script demonstrates comprehensive LineItem management using MediaPlanPy SDK v3.0.
Shows how to create, read, update, delete, and copy line items with full v3.0 field support.

v3.0 Features Demonstrated:
- Proper LineItem CRUD pattern (load → edit → update)
- Creating new line items with all v3.0 fields
- Editing dimensions (dim_custom1-10)
- Editing metrics (metric_impressions, metric_clicks, metric_custom1-10)
- Editing costs (cost_total, cost_custom1-10)
- Working with metric_formulas (dict of MetricFormula objects)
- Working with custom_properties (dict)
- Deleting line items
- Copying line items with modifications
- Bulk operations across multiple line items
- Validation patterns

Prerequisites:
- MediaPlanPy SDK v3.0.0+ installed
- Workspace created (see examples_01_create_workspace.py)
- Media plan created (see examples_03_create_mediaplan.py)

How to Run:
1. First run examples_01_create_workspace.py to create a workspace
2. Then run examples_03_create_mediaplan.py to create a media plan with line items
3. Update WORKSPACE_ID and MEDIAPLAN_ID constants below, or provide when prompted
4. Open this file in your IDE
5. Run the entire script: python examples_11_manage_lineitems.py
6. Or run individual functions by calling them from __main__

Next Steps After Running:
- Export to Excel to see custom fields (examples_06_export_mediaplan.py)
- Query line items across media plans (examples_08_list_objects.py)
- Run SQL analytics on line items (examples_09_sql_queries.py)
"""

import os
import uuid
from pathlib import Path
from datetime import date, timedelta
from decimal import Decimal

from mediaplanpy.workspace import WorkspaceManager
from mediaplanpy.models import MediaPlan, LineItem, MetricFormula


# ============================================================================
# USER CONFIGURATION
# Update these values after creating workspace and media plans
# ============================================================================

# Copy the "Workspace ID" from examples_01_create_workspace.py output
WORKSPACE_ID = "workspace_b92ee88b"

# Copy a "Media plan ID" from examples_03_create_mediaplan.py output
MEDIAPLAN_ID = "mediaplan_7b29049f"

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
        - Run examples_01_create_workspace.py first to create workspaces
        - Run examples_03_create_mediaplan.py to create media plans
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
    print(f"  - Campaign: {plan.campaign.name}")
    print(f"  - Line items: {len(plan.lineitems)}")

    return manager, plan


def load_lineitem_by_id(manager, plan):
    """
    Load a line item by ID - the proper way to retrieve line items.

    Use Case:
        When you need to edit a specific line item, always load it by ID first.
        This ensures you have the complete, current version of the line item.

    Pattern: load_lineitem() → returns complete LineItem object

    Args:
        manager: Loaded WorkspaceManager instance
        plan: Loaded MediaPlan instance

    Returns:
        Loaded LineItem instance
    """
    print("\n" + "="*60)
    print("Loading Line Item by ID")
    print("="*60)

    if not plan.lineitems:
        print("\n⚠ No line items found in media plan")
        return None

    # Get first line item ID
    lineitem_id = plan.lineitems[0].id
    print(f"\nLine item ID: {lineitem_id}")

    # Load the line item (proper CRUD method)
    print(f"Loading line item...")
    lineitem = plan.load_lineitem(lineitem_id)

    # Display details
    print(f"\n✓ Line item loaded successfully:")
    print(f"  - ID: {lineitem.id}")
    print(f"  - Name: {lineitem.name}")
    print(f"  - Channel: {lineitem.channel}")
    print(f"  - Cost: ${lineitem.cost_total:,.2f}")
    print(f"  - Start date: {lineitem.start_date}")
    print(f"  - End date: {lineitem.end_date}")

    # Show additional v3.0 fields if present
    if lineitem.metric_impressions:
        print(f"  - Impressions: {lineitem.metric_impressions:,.0f}")
    if lineitem.dim_custom1:
        print(f"  - dim_custom1: {lineitem.dim_custom1}")
    if lineitem.metric_formulas:
        print(f"  - Formulas: {len(lineitem.metric_formulas)}")
    if lineitem.custom_properties:
        print(f"  - Custom properties: {len(lineitem.custom_properties)}")

    print(f"\n✓ Load operation completed")
    return lineitem


def edit_lineitem_basic_fields(manager, plan):
    """
    Edit basic line item fields using proper CRUD pattern.

    Use Case:
        Update core fields like name, dates, channel, cost, and metrics.

    Pattern: load_lineitem() → edit fields → update_lineitem() → save()

    Args:
        manager: Loaded WorkspaceManager instance
        plan: Loaded MediaPlan instance

    Returns:
        Updated LineItem instance
    """
    print("\n" + "="*60)
    print("Editing Basic Line Item Fields")
    print("="*60)

    if not plan.lineitems:
        print("\n⚠ No line items to edit")
        return None

    # Step 1: LOAD
    lineitem_id = plan.lineitems[0].id
    print(f"\n1. Loading line item: {lineitem_id}")
    lineitem = plan.load_lineitem(lineitem_id)
    print(f"   ✓ Loaded: {lineitem.name}")

    # Capture original values
    original_name = lineitem.name
    original_cost = lineitem.cost_total
    original_channel = lineitem.channel

    print(f"\n   Original values:")
    print(f"   - Name: {original_name}")
    print(f"   - Channel: {original_channel}")
    print(f"   - Cost: ${original_cost:,.2f}")

    # Step 2: EDIT
    print(f"\n2. Editing fields...")
    lineitem.name = f"{original_name} (Updated)"
    lineitem.channel = "social"
    lineitem.cost_total = Decimal(str(float(original_cost) * 1.25))  # +25%
    lineitem.metric_impressions = Decimal("750000")
    lineitem.metric_clicks = Decimal("15000")

    print(f"   - New name: {lineitem.name}")
    print(f"   - New channel: {lineitem.channel}")
    print(f"   - New cost: ${lineitem.cost_total:,.2f} (+25%)")
    print(f"   - Impressions: {lineitem.metric_impressions:,.0f}")
    print(f"   - Clicks: {lineitem.metric_clicks:,.0f}")

    # Step 3: UPDATE (with validation)
    print(f"\n3. Updating line item with validation...")
    plan.update_lineitem(lineitem, validate=True)
    print(f"   ✓ Line item updated successfully")

    # Step 4: SAVE
    print(f"\n4. Saving media plan...")
    saved_path = plan.save(manager, overwrite=True)
    print(f"   ✓ Saved to: {saved_path}")

    # Step 5: VERIFY
    print(f"\n5. Verifying changes by reloading...")
    reloaded_plan = MediaPlan.load(manager, media_plan_id=plan.meta.id)
    reloaded_li = reloaded_plan.load_lineitem(lineitem_id)

    print(f"\n   Verification:")
    print(f"   - Name changed: {reloaded_li.name == lineitem.name}")
    print(f"   - Channel changed: {reloaded_li.channel == lineitem.channel}")
    print(f"   - Cost changed: ${reloaded_li.cost_total:,.2f}")

    print(f"\n✓ Basic field editing completed")
    return lineitem


def edit_lineitem_dimensions(manager, plan):
    """
    Edit custom dimension fields (dim_custom1-10).

    Use Case:
        Set custom dimension values for categorization, filtering, and reporting.
        These fields are configured in the Dictionary for captions.

    Args:
        manager: Loaded WorkspaceManager instance
        plan: Loaded MediaPlan instance
    """
    print("\n" + "="*60)
    print("Editing Line Item Dimensions")
    print("="*60)

    if not plan.lineitems:
        print("\n⚠ No line items to edit")
        return

    # Load line item
    lineitem_id = plan.lineitems[0].id
    lineitem = plan.load_lineitem(lineitem_id)
    print(f"\nLoaded: {lineitem.name}")

    # Edit dimensions
    print(f"\nSetting custom dimensions (dim_custom1-10)...")
    lineitem.dim_custom1 = "Premium Brands"
    lineitem.dim_custom2 = "Awareness Campaign"
    lineitem.dim_custom3 = "Q1 2025"
    lineitem.dim_custom4 = "North America"
    lineitem.dim_custom5 = "Adults 25-54"

    print(f"   - dim_custom1: {lineitem.dim_custom1}")
    print(f"   - dim_custom2: {lineitem.dim_custom2}")
    print(f"   - dim_custom3: {lineitem.dim_custom3}")
    print(f"   - dim_custom4: {lineitem.dim_custom4}")
    print(f"   - dim_custom5: {lineitem.dim_custom5}")

    # Update and save
    plan.update_lineitem(lineitem, validate=True)
    plan.save(manager, overwrite=True)

    print(f"\n✓ Dimensions updated successfully")

    print(f"\nNote: Configure dimension captions in Dictionary:")
    print(f"  mp.set_custom_field_config('dim_custom1', enabled=True, caption='Brand Category')")


def edit_lineitem_metrics_and_costs(manager, plan):
    """
    Edit metric and cost fields.

    Use Case:
        Update performance metrics (impressions, clicks, views, engagement)
        and cost breakdowns (cost_total, cost_custom1-10).

    Args:
        manager: Loaded WorkspaceManager instance
        plan: Loaded MediaPlan instance
    """
    print("\n" + "="*60)
    print("Editing Line Item Metrics and Costs")
    print("="*60)

    if not plan.lineitems:
        print("\n⚠ No line items to edit")
        return

    # Load line item
    lineitem_id = plan.lineitems[0].id
    lineitem = plan.load_lineitem(lineitem_id)
    print(f"\nLoaded: {lineitem.name}")

    # Edit standard metrics
    print(f"\nEditing standard metrics...")
    lineitem.metric_impressions = Decimal("1000000")
    lineitem.metric_clicks = Decimal("25000")
    lineitem.metric_views = Decimal("800000")
    lineitem.metric_engagement = Decimal("50000")
    lineitem.metric_conversions = Decimal("1250")

    print(f"   - Impressions: {lineitem.metric_impressions:,.0f}")
    print(f"   - Clicks: {lineitem.metric_clicks:,.0f}")
    print(f"   - Views: {lineitem.metric_views:,.0f}")
    print(f"   - Engagement: {lineitem.metric_engagement:,.0f}")
    print(f"   - Conversions: {lineitem.metric_conversions:,.0f}")

    # Edit custom metrics
    print(f"\nEditing custom metrics...")
    lineitem.metric_custom1 = Decimal("15.5")  # Brand Lift %
    lineitem.metric_custom2 = Decimal("87.3")  # Engagement Score

    print(f"   - metric_custom1: {lineitem.metric_custom1}")
    print(f"   - metric_custom2: {lineitem.metric_custom2}")

    # Edit costs
    print(f"\nEditing costs...")
    lineitem.cost_total = Decimal("25000")
    lineitem.cost_custom1 = Decimal("2000")   # Vendor Fee
    lineitem.cost_custom2 = Decimal("1500")   # Production Cost
    lineitem.cost_custom3 = Decimal("500")    # Platform Fee

    print(f"   - cost_total: ${lineitem.cost_total:,.2f}")
    print(f"   - cost_custom1: ${lineitem.cost_custom1:,.2f} (Vendor Fee)")
    print(f"   - cost_custom2: ${lineitem.cost_custom2:,.2f} (Production Cost)")
    print(f"   - cost_custom3: ${lineitem.cost_custom3:,.2f} (Platform Fee)")

    # Update and save
    plan.update_lineitem(lineitem, validate=True)
    plan.save(manager, overwrite=True)

    print(f"\n✓ Metrics and costs updated successfully")


def edit_lineitem_formulas(manager, plan):
    """
    Work with metric_formulas dictionary.

    Use Case:
        Define calculated metrics using MetricFormula objects.
        Formulas can calculate metrics from base metrics and coefficients.

    Args:
        manager: Loaded WorkspaceManager instance
        plan: Loaded MediaPlan instance
    """
    print("\n" + "="*60)
    print("Working with Metric Formulas")
    print("="*60)

    if not plan.lineitems:
        print("\n⚠ No line items to edit")
        return

    # Load line item
    lineitem_id = plan.lineitems[0].id
    lineitem = plan.load_lineitem(lineitem_id)
    print(f"\nLoaded: {lineitem.name}")

    # Initialize formulas dict if needed
    if lineitem.metric_formulas is None:
        lineitem.metric_formulas = {}

    # Add CPM formula
    print(f"\nAdding CPM formula...")
    lineitem.metric_formulas["metric_impressions"] = MetricFormula(
        formula_type="cost_per_unit",
        base_metric="cost_total",
        coefficient=0.008,
        comments="metric_impressions = cost_total / cpm * 1000"
    )
    print(f"   ✓ Added: CPM formula (coefficient=8.0)")

    # Add CTR formula
    print(f"\nAdding CTR formula...")
    lineitem.metric_formulas["metric_clicks"] = MetricFormula(
        formula_type="conversion_rate",
        base_metric="metric_impressions",
        coefficient=0.025,  # 2.5% CTR
        comments="metric_clicks =  metric_impressions * CTR"
    )
    print(f"   ✓ Added: CTR formula (coefficient=0.025)")

    # Add conversion rate formula
    print(f"\nAdding conversion rate formula...")
    lineitem.metric_formulas["metric_conversions"] = MetricFormula(
        formula_type="conversion_rate",
        base_metric="metric_clicks",
        coefficient=0.05,  # 5% conversion rate
        comments="metric_comversions = metric_clicks"
    )
    print(f"   ✓ Added: Conversion rate formula (coefficient=0.05)")

    print(f"\nTotal formulas: {len(lineitem.metric_formulas)}")
    for name, formula in lineitem.metric_formulas.items():
        print(f"   - {name}: {formula.formula_type} from {formula.base_metric}")

    # Update and save
    plan.update_lineitem(lineitem, validate=True)
    plan.save(manager, overwrite=True)

    print(f"\n✓ Formulas updated successfully")

    print(f"\nNote: Future enhancement will support automatic recalculation")
    print(f"See: docs/formula_recalculation_design.md")


def edit_lineitem_custom_properties(manager, plan):
    """
    Work with custom_properties dictionary.

    Use Case:
        Store arbitrary key-value metadata on line items.
        Useful for custom workflows, integrations, and extensibility.

    Args:
        manager: Loaded WorkspaceManager instance
        plan: Loaded MediaPlan instance
    """
    print("\n" + "="*60)
    print("Working with Custom Properties")
    print("="*60)

    if not plan.lineitems:
        print("\n⚠ No line items to edit")
        return

    # Load line item
    lineitem_id = plan.lineitems[0].id
    lineitem = plan.load_lineitem(lineitem_id)
    print(f"\nLoaded: {lineitem.name}")

    # Initialize custom_properties if needed
    if lineitem.custom_properties is None:
        lineitem.custom_properties = {}

    # Add properties
    print(f"\nAdding custom properties...")
    lineitem.custom_properties["campaign_tier"] = "premium"
    lineitem.custom_properties["optimization_status"] = "active"
    lineitem.custom_properties["targeting_strategy"] = "lookalike"
    lineitem.custom_properties["created_by_tool"] = "MediaPlanPy v3.0"
    lineitem.custom_properties["notes"] = "High-performing line item, monitor daily"

    print(f"   Total properties: {len(lineitem.custom_properties)}")
    for key, value in lineitem.custom_properties.items():
        print(f"   - {key}: {value}")

    # Update and save
    plan.update_lineitem(lineitem, validate=True)
    plan.save(manager, overwrite=True)

    print(f"\n✓ Custom properties updated successfully")


def create_new_lineitem(manager, plan):
    """
    Create a new line item from scratch.

    Use Case:
        Add new line items to an existing media plan.
        Supports both dictionary format and LineItem objects.

    Pattern: create_lineitem() with dict or LineItem object

    Args:
        manager: Loaded WorkspaceManager instance
        plan: Loaded MediaPlan instance

    Returns:
        Newly created LineItem instance
    """
    print("\n" + "="*60)
    print("Creating New Line Item")
    print("="*60)

    print(f"\nMedia plan: {plan.meta.name}")
    print(f"Current line items: {len(plan.lineitems)}")

    # Method 1: Create from dictionary
    print(f"\nCreating line item from dictionary...")

    new_lineitem_dict = {
        "name": "New Social Media Campaign",
        "channel": "social",
        "start_date": plan.campaign.start_date + timedelta(days=30),
        "end_date": plan.campaign.end_date - timedelta(days=30),
        "cost_total": Decimal("15000"),
        "cost_currency": "USD",
        "metric_impressions": Decimal("500000"),
        "metric_clicks": Decimal("10000"),
        "dim_custom1": "Social Media",
        "dim_custom2": "Consideration",
        "custom_properties": {
            "platform": "Meta",
            "format": "Video"
        }
    }

    # Create the line item
    new_lineitem = plan.create_lineitem(new_lineitem_dict, validate=True)

    print(f"✓ Line item created:")
    print(f"  - ID: {new_lineitem.id}")
    print(f"  - Name: {new_lineitem.name}")
    print(f"  - Channel: {new_lineitem.channel}")
    print(f"  - Cost: ${new_lineitem.cost_total:,.2f}")
    print(f"  - Dates: {new_lineitem.start_date} to {new_lineitem.end_date}")

    # Save
    print(f"\nSaving media plan...")
    plan.save(manager, overwrite=True)
    print(f"✓ Saved successfully")

    # Verify
    print(f"\nVerifying...")
    print(f"  - Total line items now: {len(plan.lineitems)}")

    print(f"\n✓ Line item creation completed")
    return new_lineitem


def copy_lineitem_with_modifications(manager, plan):
    """
    Copy an existing line item using the copy_lineitem() helper method.

    Use Case:
        Duplicate a line item and modify specific fields (e.g., different dates,
        budget, or targeting). Useful for creating similar campaigns.

    Pattern: plan.copy_lineitem() → automatic deepcopy with modifications

    Args:
        manager: Loaded WorkspaceManager instance
        plan: Loaded MediaPlan instance

    Returns:
        Newly created LineItem (copy)
    """
    print("\n" + "="*60)
    print("Copying Line Item with Modifications")
    print("="*60)

    if not plan.lineitems:
        print("\n⚠ No line items to copy")
        return None

    # Load source line item for reference
    source_id = plan.lineitems[0].id
    source_li = plan.load_lineitem(source_id)
    print(f"\nSource line item:")
    print(f"  - ID: {source_li.id}")
    print(f"  - Name: {source_li.name}")
    print(f"  - Cost: ${source_li.cost_total:,.2f}")
    if source_li.metric_impressions:
        print(f"  - Impressions: {source_li.metric_impressions:,.0f}")

    # METHOD 1: Simple copy with new name
    print(f"\n" + "-"*60)
    print("Method 1: Simple copy with new name")
    print("-"*60)

    simple_copy = plan.copy_lineitem(
        source_id,
        new_name="Simple Copy Example"
    )

    print(f"✓ Simple copy created:")
    print(f"  - New ID: {simple_copy.id}")
    print(f"  - Name: {simple_copy.name}")
    print(f"  - Cost: ${simple_copy.cost_total:,.2f} (same as source)")

    # METHOD 2: Copy with modifications (scaled down)
    print(f"\n" + "-"*60)
    print("Method 2: Copy with modifications (scale down 20%)")
    print("-"*60)

    scaled_copy = plan.copy_lineitem(
        source_id,
        modifications={
            "name": f"{source_li.name} (Scaled Copy)",
            "cost_total": source_li.cost_total * Decimal("0.8"),  # -20%
            "metric_impressions": source_li.metric_impressions * Decimal("0.8") if source_li.metric_impressions else None,
            "metric_clicks": source_li.metric_clicks * Decimal("0.8") if source_li.metric_clicks else None,
            "custom_properties": {
                "copied_from": source_li.id,
                "copy_type": "scaled_down",
                "scaling_factor": 0.8
            }
        }
    )

    print(f"✓ Scaled copy created:")
    print(f"  - New ID: {scaled_copy.id}")
    print(f"  - Name: {scaled_copy.name}")
    print(f"  - Cost: ${scaled_copy.cost_total:,.2f} (-20%)")
    if scaled_copy.metric_impressions:
        print(f"  - Impressions: {scaled_copy.metric_impressions:,.0f} (-20%)")

    # Save all changes
    print(f"\n" + "-"*60)
    print("Saving media plan...")
    print("-"*60)
    plan.save(manager, overwrite=True)
    print(f"✓ Saved successfully")

    # Summary
    print(f"\nSummary:")
    print(f"  - Original line items: 1")
    print(f"  - Copies created: 2")
    print(f"  - Total line items now: {len(plan.lineitems)}")

    print(f"\nKey Benefits of copy_lineitem():")
    print(f"  ✓ Automatic deepcopy (no manual field copying)")
    print(f"  ✓ Only modify fields you need to change")
    print(f"  ✓ Auto-generates new ID")
    print(f"  ✓ Clean, readable code")
    print(f"  ✓ Date validation warnings (not errors)")

    return scaled_copy


def delete_lineitem(manager, plan):
    """
    Delete a line item from a media plan.

    Use Case:
        Remove line items that are no longer needed.
        Always verify before deleting in production scenarios.

    Pattern: delete_lineitem(line_item_id)

    Args:
        manager: Loaded WorkspaceManager instance
        plan: Loaded MediaPlan instance
    """
    print("\n" + "="*60)
    print("Deleting Line Item")
    print("="*60)

    if len(plan.lineitems) < 2:
        print("\n⚠ Need at least 2 line items to demonstrate deletion")
        print("   (keeping at least one line item in the plan)")
        return

    # Show current state
    print(f"\nCurrent line items: {len(plan.lineitems)}")
    for li in plan.lineitems:
        print(f"  - {li.id}: {li.name}")

    # Select last line item for deletion
    lineitem_to_delete = plan.lineitems[-1]
    delete_id = lineitem_to_delete.id
    delete_name = lineitem_to_delete.name

    print(f"\nDeleting line item:")
    print(f"  - ID: {delete_id}")
    print(f"  - Name: {delete_name}")

    # Confirm in real scenario
    print(f"\n⚠ In production, always confirm deletions with users")

    # Delete
    print(f"\nDeleting...")
    success = plan.delete_lineitem(delete_id, validate=False)

    if success:
        print(f"✓ Line item deleted successfully")
    else:
        print(f"✗ Failed to delete line item")
        return

    # Save
    print(f"\nSaving media plan...")
    plan.save(manager, overwrite=True)
    print(f"✓ Saved successfully")

    # Verify
    print(f"\nVerification:")
    print(f"  - Line items before: {len(plan.lineitems) + 1}")
    print(f"  - Line items after: {len(plan.lineitems)}")

    print(f"\n✓ Deletion completed")


def bulk_edit_lineitems(manager, plan):
    """
    Edit multiple line items in bulk.

    Use Case:
        Apply changes to multiple line items at once (e.g., update dimensions,
        adjust costs, set properties across all line items).

    Pattern: Loop through load → edit → update for each line item

    Args:
        manager: Loaded WorkspaceManager instance
        plan: Loaded MediaPlan instance
    """
    print("\n" + "="*60)
    print("Bulk Editing Line Items")
    print("="*60)

    if not plan.lineitems:
        print("\n⚠ No line items to edit")
        return

    print(f"\nTotal line items: {len(plan.lineitems)}")

    # Bulk operation: Update all line items with new dimension
    print(f"\nBulk operation: Setting dim_custom5='Q1 2025' on all line items...")

    updated_count = 0
    for li in plan.lineitems:
        # Load
        lineitem = plan.load_lineitem(li.id)

        # Edit
        lineitem.dim_custom5 = "Q1 2025"

        # Update
        plan.update_lineitem(lineitem, validate=True)
        updated_count += 1
        print(f"   ✓ Updated: {lineitem.name}")

    print(f"\n✓ Bulk edit completed: {updated_count} line items updated")

    # Save once after all edits
    print(f"\nSaving media plan...")
    plan.save(manager, overwrite=True)
    print(f"✓ Saved successfully")


def validation_patterns(manager, plan):
    """
    Demonstrate validation patterns for line item operations.

    Use Case:
        Understand validation options and error handling when working
        with line items.

    Args:
        manager: Loaded WorkspaceManager instance
        plan: Loaded MediaPlan instance
    """
    print("\n" + "="*60)
    print("Validation Patterns")
    print("="*60)

    if not plan.lineitems:
        print("\n⚠ No line items to validate")
        return

    # Load line item
    lineitem = plan.load_lineitem(plan.lineitems[0].id)
    print(f"\nLoaded: {lineitem.name}")

    # Pattern 1: Update with validation (recommended)
    print(f"\n1. Update with validation (validate=True):")
    print(f"   - Validates line item fields")
    print(f"   - Validates dates against campaign")
    print(f"   - Raises ValidationError if invalid")
    print(f"   - RECOMMENDED for production use")

    try:
        plan.update_lineitem(lineitem, validate=True)
        print(f"   ✓ Validation passed")
    except Exception as e:
        print(f"   ✗ Validation failed: {e}")

    # Pattern 2: Update without validation (use with caution)
    print(f"\n2. Update without validation (validate=False):")
    print(f"   - Skips validation checks")
    print(f"   - Faster but riskier")
    print(f"   - Use only when you're certain data is valid")

    plan.update_lineitem(lineitem, validate=False)
    print(f"   ✓ Updated without validation")

    # Pattern 3: Create with validation
    print(f"\n3. Create with validation:")
    print(f"   - Validates on creation")
    print(f"   - Prevents invalid line items from being added")

    try:
        test_li = {
            "name": "Test Line Item",
            "channel": "display",
            "start_date": plan.campaign.start_date,
            "end_date": plan.campaign.end_date,
            "cost_total": Decimal("1000")
        }
        plan.create_lineitem(test_li, validate=True)
        print(f"   ✓ Creation validation passed")

        # Clean up
        plan.delete_lineitem(plan.lineitems[-1].id)
    except Exception as e:
        print(f"   ✗ Creation validation failed: {e}")

    print(f"\n✓ Validation patterns demonstrated")


if __name__ == "__main__":
    print("="*60)
    print("MediaPlanPy v3.0 - Manage Line Items Examples")
    print("="*60)

    # Load workspace and plan ONCE
    print("\nLoading workspace and media plan...")
    manager, plan = load_workspace_and_plan()

    if manager is None or plan is None:
        print("\nNo workspace or media plan loaded. Exiting.")
        print("\nTo run these examples:")
        print("  1. Run examples_01_create_workspace.py first")
        print("  2. Run examples_03_create_mediaplan.py to create plans with line items")
        print("  3. Update WORKSPACE_ID and MEDIAPLAN_ID at top of this file")
        print("  4. Or provide values when prompted")
        exit(0)

    print("\n=== Example 1: Load Line Item by ID ===")
    loaded_li = load_lineitem_by_id(manager, plan)

    print("\n=== Example 2: Edit Basic Fields ===")
    # Reload plan to get fresh state
    plan = MediaPlan.load(manager, media_plan_id=plan.meta.id)
    edit_lineitem_basic_fields(manager, plan)

    print("\n=== Example 3: Edit Dimensions ===")
    plan = MediaPlan.load(manager, media_plan_id=plan.meta.id)
    edit_lineitem_dimensions(manager, plan)

    print("\n=== Example 4: Edit Metrics and Costs ===")
    plan = MediaPlan.load(manager, media_plan_id=plan.meta.id)
    edit_lineitem_metrics_and_costs(manager, plan)

    print("\n=== Example 5: Work with Metric Formulas ===")
    plan = MediaPlan.load(manager, media_plan_id=plan.meta.id)
    edit_lineitem_formulas(manager, plan)

    print("\n=== Example 6: Work with Custom Properties ===")
    plan = MediaPlan.load(manager, media_plan_id=plan.meta.id)
    edit_lineitem_custom_properties(manager, plan)

    print("\n=== Example 7: Create New Line Item ===")
    plan = MediaPlan.load(manager, media_plan_id=plan.meta.id)
    create_new_lineitem(manager, plan)

    print("\n=== Example 8: Copy Line Item with Modifications ===")
    plan = MediaPlan.load(manager, media_plan_id=plan.meta.id)
    copy_lineitem_with_modifications(manager, plan)

    print("\n=== Example 9: Delete Line Item ===")
    plan = MediaPlan.load(manager, media_plan_id=plan.meta.id)
    delete_lineitem(manager, plan)

    print("\n=== Example 10: Bulk Edit Line Items ===")
    plan = MediaPlan.load(manager, media_plan_id=plan.meta.id)
    bulk_edit_lineitems(manager, plan)

    print("\n=== Example 11: Validation Patterns ===")
    plan = MediaPlan.load(manager, media_plan_id=plan.meta.id)
    validation_patterns(manager, plan)

    print("\n" + "="*60)
    print("Manage Line Items Examples Completed!")
    print("="*60)

    print(f"\nWhat We Demonstrated:")
    print(f"  1. Loading line items by ID (proper CRUD pattern)")
    print(f"  2. Editing basic fields (name, channel, cost, dates)")
    print(f"  3. Editing dimensions (dim_custom1-10)")
    print(f"  4. Editing metrics (standard and custom)")
    print(f"  5. Editing costs (cost_total, cost_custom1-10)")
    print(f"  6. Working with metric_formulas (dict of MetricFormula objects)")
    print(f"  7. Working with custom_properties (dict for extensibility)")
    print(f"  8. Creating new line items from scratch")
    print(f"  9. Copying line items with modifications")
    print(f" 10. Deleting line items")
    print(f" 11. Bulk editing multiple line items")
    print(f" 12. Validation patterns (validate=True/False)")

    print(f"\nKey Patterns:")
    print(f"  - Always use load_lineitem() → edit → update_lineitem() pattern")
    print(f"  - Validate by default (validate=True)")
    print(f"  - Save media plan after updates (plan.save())")
    print(f"  - Reload to verify changes")

    print(f"\nNext Steps:")
    print(f"  - Configure Dictionary for custom field captions (examples_05)")
    print(f"  - Export to Excel to see all fields (examples_06)")
    print(f"  - Query line items across plans (examples_08)")
    print(f"  - Run SQL analytics (examples_09)")
