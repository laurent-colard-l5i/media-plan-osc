"""
MediaPlanPy Examples - Manage Dictionary

This script demonstrates comprehensive Dictionary management using MediaPlanPy SDK v3.0.
Shows how to configure custom fields, set captions, and define formulas for dimensions, metrics, and costs.

v3.0 Features Demonstrated:
- Configuring custom dimensions with scopes (meta, campaign, lineitem)
- Enabling custom metrics with optional formulas
- Enabling custom costs
- Configuring standard metric formulas
- Querying enabled fields and their captions
- How Dictionary configuration affects line items and exports

What is Dictionary?
The Dictionary is a configuration layer that allows you to:
- Enable/disable custom fields (dim_custom1-10, metric_custom1-10, cost_custom1-10)
- Set human-readable captions that appear in Excel exports and BI tools
- Define formulas for calculated metrics (both standard and custom)
- Support scoped dimensions (same field name at meta/campaign/lineitem levels)

Prerequisites:
- MediaPlanPy SDK v3.0.0+ installed
- Workspace created (see examples_01_create_workspace.py)
- Media plan created with line items (see examples_03_create_mediaplan.py)

How to Run:
1. First run examples_01_create_workspace.py to create a workspace
2. Then run examples_03_create_mediaplan.py to create a media plan with line items
3. Update WORKSPACE_ID and MEDIAPLAN_ID constants below, or provide when prompted
4. Open this file in your IDE
5. Run the entire script: python examples_12_manage_dictionary.py
6. Or run individual functions by calling them from __main__

Next Steps After Running:
- Use enabled fields in line items (examples_11_manage_lineitems.py)
- Export to Excel to see custom field captions as column headers (examples_06_export_mediaplan.py)
- Query enabled fields for BI integrations (examples_08_list_objects.py)
"""

import os
from pathlib import Path
from decimal import Decimal

from mediaplanpy.workspace import WorkspaceManager
from mediaplanpy.models import MediaPlan


# ============================================================================
# USER CONFIGURATION
# Update these values after creating workspace and media plans
# ============================================================================

# Copy the "Workspace ID" from examples_01_create_workspace.py output
WORKSPACE_ID = "workspace_b92ee88b"

# Copy a "Media plan ID" from examples_03_create_mediaplan.py output
MEDIAPLAN_ID = "mediaplan_7695a631"
#MEDIAPLAN_ID = "mediaplan_7b29049f"

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


def configure_custom_dimensions(manager, plan):
    """
    Configure custom dimension fields with scopes.

    Use Case:
        Enable and caption custom dimensions at different levels (meta, campaign, lineitem).
        Same field name (e.g., dim_custom1) can have different meanings at different levels.

    v3.0 Feature: Scoped dimensions allow dim_custom1 at meta, campaign, and lineitem
                  to be configured independently.

    Args:
        manager: Loaded WorkspaceManager instance
        plan: Loaded MediaPlan instance
    """
    print("\n" + "="*60)
    print("Configuring Custom Dimensions (Scoped)")
    print("="*60)

    print("\nCustom dimensions allow you to add categorization and filtering fields")
    print("to your media plans at three different levels:")
    print("  - Meta level: Organization/portfolio dimensions")
    print("  - Campaign level: Campaign-specific attributes")
    print("  - Line item level: Granular line item categorization")

    # Configure lineitem dimensions (default scope)
    print("\n" + "-"*60)
    print("1. Configuring Line Item Dimensions")
    print("-"*60)

    plan.set_custom_field_config("dim_custom1", enabled=True, caption="Brand Category", scope="lineitem")
    print("   ✓ dim_custom1 (lineitem): 'Brand Category'")

    plan.set_custom_field_config("dim_custom2", enabled=True, caption="Campaign Type", scope="lineitem")
    print("   ✓ dim_custom2 (lineitem): 'Campaign Type'")

    plan.set_custom_field_config("dim_custom3", enabled=True, caption="Media Format", scope="lineitem")
    print("   ✓ dim_custom3 (lineitem): 'Media Format'")

    # Configure meta dimensions
    print("\n" + "-"*60)
    print("2. Configuring Meta Dimensions")
    print("-"*60)

    plan.set_custom_field_config("dim_custom1", enabled=True, caption="Region", scope="meta")
    print("   ✓ dim_custom1 (meta): 'Region'")

    plan.set_custom_field_config("dim_custom2", enabled=True, caption="Business Unit", scope="meta")
    print("   ✓ dim_custom2 (meta): 'Business Unit'")

    # Configure campaign dimensions
    print("\n" + "-"*60)
    print("3. Configuring Campaign Dimensions")
    print("-"*60)

    plan.set_custom_field_config("dim_custom1", enabled=True, caption="Segment", scope="campaign")
    print("   ✓ dim_custom1 (campaign): 'Segment'")

    plan.set_custom_field_config("dim_custom2", enabled=True, caption="Product Line", scope="campaign")
    print("   ✓ dim_custom2 (campaign): 'Product Line'")

    # Query configurations
    print("\n" + "-"*60)
    print("4. Querying Dimension Configurations")
    print("-"*60)

    # Get specific configs
    lineitem_dim1 = plan.get_custom_field_config("dim_custom1", scope="lineitem")
    meta_dim1 = plan.get_custom_field_config("dim_custom1", scope="meta")
    campaign_dim1 = plan.get_custom_field_config("dim_custom1", scope="campaign")

    print(f"\n   dim_custom1 at different scopes:")
    print(f"   - lineitem: {lineitem_dim1['caption']}")
    print(f"   - meta: {meta_dim1['caption']}")
    print(f"   - campaign: {campaign_dim1['caption']}")

    # Save
    plan.save(manager, overwrite=True)
    print("\n✓ Custom dimensions configured and saved")


def configure_custom_metrics(manager, plan):
    """
    Configure custom metric fields with optional formulas.

    Use Case:
        Enable custom metrics for KPIs, calculated values, or business-specific measurements.
        Optionally define formulas for automatic calculation.

    Args:
        manager: Loaded WorkspaceManager instance
        plan: Loaded MediaPlan instance
    """
    print("\n" + "="*60)
    print("Configuring Custom Metrics")
    print("="*60)

    print("\nCustom metrics allow you to track business-specific KPIs")
    print("beyond the standard metrics (impressions, clicks, etc.)")

    # Custom metrics without formulas
    print("\n" + "-"*60)
    print("1. Custom Metrics Without Formulas")
    print("-"*60)
    print("   (Values will be entered manually)")

    plan.set_custom_field_config(
        "metric_custom1",
        enabled=True,
        caption="Brand Lift %"
    )
    print("   ✓ metric_custom1: 'Brand Lift %'")

    plan.set_custom_field_config(
        "metric_custom2",
        enabled=True,
        caption="Engagement Score"
    )
    print("   ✓ metric_custom2: 'Engagement Score'")

    # Custom metrics with formulas
    print("\n" + "-"*60)
    print("2. Custom Metrics With Formulas")
    print("-"*60)
    print("   (Values can be auto-calculated in future)")

    plan.set_custom_field_config(
        "metric_custom3",
        enabled=True,
        caption="Custom CPM",
        formula_type="cost_per_unit",
        base_metric="cost_total"
    )
    print("   ✓ metric_custom3: 'Custom CPM' (formula: cost_per_unit from cost_total)")

    plan.set_custom_field_config(
        "metric_custom4",
        enabled=True,
        caption="Custom CTR",
        formula_type="conversion_rate",
        base_metric="metric_impressions"
    )
    print("   ✓ metric_custom4: 'Custom CTR' (formula: conversion_rate from metric_impressions)")

    # Query configuration
    print("\n" + "-"*60)
    print("3. Querying Custom Metric Configurations")
    print("-"*60)

    metric1 = plan.get_custom_field_config("metric_custom1")
    metric3 = plan.get_custom_field_config("metric_custom3")

    print(f"\n   metric_custom1 (manual):")
    print(f"   - Caption: {metric1['caption']}")
    print(f"   - Formula: {metric1.get('formula_type', 'None')}")

    print(f"\n   metric_custom3 (with formula):")
    print(f"   - Caption: {metric3['caption']}")
    print(f"   - Formula: {metric3.get('formula_type')}")
    print(f"   - Base metric: {metric3.get('base_metric')}")

    # Save
    plan.save(manager, overwrite=True)
    print("\n✓ Custom metrics configured and saved")


def configure_custom_costs(manager, plan):
    """
    Configure custom cost fields.

    Use Case:
        Enable custom cost breakdowns beyond cost_total (e.g., vendor fees,
        production costs, platform fees).

    Args:
        manager: Loaded WorkspaceManager instance
        plan: Loaded MediaPlan instance
    """
    print("\n" + "="*60)
    print("Configuring Custom Costs")
    print("="*60)

    print("\nCustom costs allow you to break down costs beyond cost_total")
    print("for detailed budget tracking and reporting.")

    plan.set_custom_field_config("cost_custom1", enabled=True, caption="Vendor Fee")
    print("   ✓ cost_custom1: 'Vendor Fee'")

    plan.set_custom_field_config("cost_custom2", enabled=True, caption="Production Cost")
    print("   ✓ cost_custom2: 'Production Cost'")

    plan.set_custom_field_config("cost_custom3", enabled=True, caption="Platform Fee")
    print("   ✓ cost_custom3: 'Platform Fee'")

    plan.set_custom_field_config("cost_custom4", enabled=True, caption="Agency Commission")
    print("   ✓ cost_custom4: 'Agency Commission'")

    # Save
    plan.save(manager, overwrite=True)
    print("\n✓ Custom costs configured and saved")


def configure_standard_metric_formulas(manager, plan):
    """
    Configure formulas for standard metrics.

    Use Case:
        Define how standard metrics (impressions, clicks, etc.) should be
        calculated from base metrics. Useful for forecasting and planning.

    Args:
        manager: Loaded WorkspaceManager instance
        plan: Loaded MediaPlan instance
    """
    print("\n" + "="*60)
    print("Configuring Standard Metric Formulas")
    print("="*60)

    print("\nStandard metric formulas define how metrics like impressions")
    print("and clicks can be calculated from cost and coefficients (CPM, CPC).")
    print("\nNote: Auto-calculation will be supported in a future release.")
    print("See: docs/formula_recalculation_design.md")

    # Configure impressions formula
    print("\n" + "-"*60)
    print("1. Impressions from Cost and CPM")
    print("-"*60)

    plan.set_standard_metric_formula(
        "metric_impressions",
        formula_type="cost_per_unit",
        base_metric="cost_total"
    )
    print("   ✓ metric_impressions: cost_per_unit from cost_total")
    print("      Formula: impressions = (cost_total / CPM) * 1000")

    # Configure clicks formula
    print("\n" + "-"*60)
    print("2. Clicks from Impressions and CTR")
    print("-"*60)

    plan.set_standard_metric_formula(
        "metric_clicks",
        formula_type="conversion_rate",
        base_metric="metric_impressions"
    )
    print("   ✓ metric_clicks: conversion_rate from metric_impressions")
    print("      Formula: clicks = impressions * CTR")

    # Configure conversions formula
    print("\n" + "-"*60)
    print("3. Conversions from Clicks and Conversion Rate")
    print("-"*60)

    plan.set_standard_metric_formula(
        "metric_conversions",
        formula_type="conversion_rate",
        base_metric="metric_clicks"
    )
    print("   ✓ metric_conversions: conversion_rate from metric_clicks")
    print("      Formula: conversions = clicks * conversion_rate")

    # Query formula configuration
    print("\n" + "-"*60)
    print("4. Querying Formula Configurations")
    print("-"*60)

    impressions_formula = plan.get_standard_metric_formula("metric_impressions")
    clicks_formula = plan.get_standard_metric_formula("metric_clicks")

    print(f"\n   metric_impressions formula:")
    print(f"   - Type: {impressions_formula['formula_type']}")
    print(f"   - Base metric: {impressions_formula['base_metric']}")

    print(f"\n   metric_clicks formula:")
    print(f"   - Type: {clicks_formula['formula_type']}")
    print(f"   - Base metric: {clicks_formula['base_metric']}")

    # Save
    plan.save(manager, overwrite=True)
    print("\n✓ Standard metric formulas configured and saved")


def use_custom_fields_in_lineitems(manager, plan):
    """
    Use configured custom fields in line items.

    Use Case:
        After configuring Dictionary, set custom field values on line items.
        Shows how Dictionary captions improve data readability.

    Args:
        manager: Loaded WorkspaceManager instance
        plan: Loaded MediaPlan instance
    """
    print("\n" + "="*60)
    print("Using Custom Fields in Line Items")
    print("="*60)

    if not plan.lineitems:
        print("\n⚠ No line items found. Create line items first.")
        print("   Run: examples_03_create_mediaplan.py")
        return

    # Load first line item
    lineitem = plan.load_lineitem(plan.lineitems[0].id)
    print(f"\nLoaded line item: {lineitem.name}")

    # Set custom dimension values
    print("\n" + "-"*60)
    print("1. Setting Custom Dimension Values")
    print("-"*60)

    lineitem.dim_custom1 = "Premium Brands"
    lineitem.dim_custom2 = "Awareness"
    lineitem.dim_custom3 = "Video"

    print(f"   ✓ dim_custom1 (Brand Category): {lineitem.dim_custom1}")
    print(f"   ✓ dim_custom2 (Campaign Type): {lineitem.dim_custom2}")
    print(f"   ✓ dim_custom3 (Media Format): {lineitem.dim_custom3}")

    # Set custom metric values
    print("\n" + "-"*60)
    print("2. Setting Custom Metric Values")
    print("-"*60)

    lineitem.metric_custom1 = Decimal("15.5")  # Brand Lift %
    lineitem.metric_custom2 = Decimal("87.3")  # Engagement Score

    print(f"   ✓ metric_custom1 (Brand Lift %): {lineitem.metric_custom1}%")
    print(f"   ✓ metric_custom2 (Engagement Score): {lineitem.metric_custom2}")

    # Set custom cost values
    print("\n" + "-"*60)
    print("3. Setting Custom Cost Values")
    print("-"*60)

    lineitem.cost_custom1 = Decimal("5000")   # Vendor Fee
    lineitem.cost_custom2 = Decimal("3500")   # Production Cost
    lineitem.cost_custom3 = Decimal("1200")   # Platform Fee

    print(f"   ✓ cost_custom1 (Vendor Fee): ${lineitem.cost_custom1:,.2f}")
    print(f"   ✓ cost_custom2 (Production Cost): ${lineitem.cost_custom2:,.2f}")
    print(f"   ✓ cost_custom3 (Platform Fee): ${lineitem.cost_custom3:,.2f}")

    # Update and save
    print("\n" + "-"*60)
    print("4. Saving Changes")
    print("-"*60)

    plan.update_lineitem(lineitem, validate=True)
    plan.save(manager, overwrite=True)
    print("   ✓ Line item updated and saved")

    # Verify
    print("\n" + "-"*60)
    print("5. Verifying by Reloading")
    print("-"*60)

    reloaded_plan = MediaPlan.load(manager, media_plan_id=plan.meta.id)
    reloaded_li = reloaded_plan.load_lineitem(lineitem.id)

    print(f"\n   Verified values:")
    print(f"   - Brand Category: {reloaded_li.dim_custom1}")
    print(f"   - Brand Lift %: {reloaded_li.metric_custom1}")
    print(f"   - Vendor Fee: ${reloaded_li.cost_custom1:,.2f}")

    print("\n✓ Custom fields successfully used in line items")


def query_enabled_fields(manager, plan):
    """
    Query all enabled custom fields.

    Use Case:
        Retrieve all enabled fields and their captions for use in BI tools,
        exports, or dynamic UI generation.

    Args:
        manager: Loaded WorkspaceManager instance
        plan: Loaded MediaPlan instance
    """
    print("\n" + "="*60)
    print("Querying Enabled Custom Fields")
    print("="*60)

    # Get all enabled fields
    enabled_fields = plan.get_enabled_custom_fields()

    print(f"\nTotal enabled fields: {len(enabled_fields)}")

    # Group by category
    dimensions = {k: v for k, v in enabled_fields.items() if k.startswith('dim_custom') or 'dim_custom' in k}
    metrics = {k: v for k, v in enabled_fields.items() if k.startswith('metric_custom')}
    costs = {k: v for k, v in enabled_fields.items() if k.startswith('cost_custom')}

    # Display dimensions
    print("\n" + "-"*60)
    print(f"Custom Dimensions ({len(dimensions)}):")
    print("-"*60)
    for field_name, caption in sorted(dimensions.items()):
        print(f"  {field_name:<30} → {caption}")

    # Display metrics
    print("\n" + "-"*60)
    print(f"Custom Metrics ({len(metrics)}):")
    print("-"*60)
    for field_name, caption in sorted(metrics.items()):
        print(f"  {field_name:<30} → {caption}")

    # Display costs
    print("\n" + "-"*60)
    print(f"Custom Costs ({len(costs)}):")
    print("-"*60)
    for field_name, caption in sorted(costs.items()):
        print(f"  {field_name:<30} → {caption}")

    print("\n✓ Field query completed")

    print("\nHow This Helps:")
    print("  ✓ Excel exports use these captions as column headers")
    print("  ✓ BI tools can display human-readable field names")
    print("  ✓ Dynamic UIs can be generated from enabled fields")
    print("  ✓ API integrations know which fields are active")


if __name__ == "__main__":
    print("="*60)
    print("MediaPlanPy v3.0 - Manage Dictionary Examples")
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

    print("\n=== Example 1: Configure Custom Dimensions ===")
    configure_custom_dimensions(manager, plan)

    print("\n=== Example 2: Configure Custom Metrics ===")
    plan = MediaPlan.load(manager, media_plan_id=plan.meta.id)
    configure_custom_metrics(manager, plan)

    print("\n=== Example 3: Configure Custom Costs ===")
    plan = MediaPlan.load(manager, media_plan_id=plan.meta.id)
    configure_custom_costs(manager, plan)

    print("\n=== Example 4: Configure Standard Metric Formulas ===")
    plan = MediaPlan.load(manager, media_plan_id=plan.meta.id)
    configure_standard_metric_formulas(manager, plan)

    print("\n=== Example 5: Use Custom Fields in Line Items ===")
    plan = MediaPlan.load(manager, media_plan_id=plan.meta.id)
    use_custom_fields_in_lineitems(manager, plan)

    print("\n=== Example 6: Query Enabled Fields ===")
    plan = MediaPlan.load(manager, media_plan_id=plan.meta.id)
    query_enabled_fields(manager, plan)

    print("\n" + "="*60)
    print("Manage Dictionary Examples Completed!")
    print("="*60)

    print(f"\nWhat We Demonstrated:")
    print(f"  1. Configured custom dimensions with scopes (meta/campaign/lineitem)")
    print(f"  2. Configured custom metrics (with and without formulas)")
    print(f"  3. Configured custom costs")
    print(f"  4. Configured standard metric formulas")
    print(f"  5. Used custom fields in line items")
    print(f"  6. Queried all enabled fields and their captions")

    print(f"\nKey Concepts:")
    print(f"  - Dictionary is a configuration layer for custom fields")
    print(f"  - Scoped dimensions allow same field name at different levels")
    print(f"  - Captions appear in Excel exports and BI tools")
    print(f"  - Formulas enable future auto-calculation features")

    print(f"\nNext Steps:")
    print(f"  - Export to Excel to see custom field captions (examples_06)")
    print(f"  - Use custom fields in line items (examples_11)")
    print(f"  - Query enabled fields for integrations (examples_08)")
