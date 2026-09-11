"""
MediaPlanPy Examples - Edit Media Plan

This script demonstrates how to edit media plans and use advanced save options using MediaPlanPy SDK v3.0.
Shows how to modify basic properties, v3.0 features, and manage plan versions.

v3.0 Features Demonstrated:
- Editing basic properties (name, budget, objective)
- Modifying v3.0 array-based models (target_audiences, target_locations)
- Adding new objects to arrays
- Updating KPIs and custom dimensions
- Merging custom_properties dictionaries
- Proper LineItem CRUD pattern (load → edit → update)
- Advanced save options (overwrite, set_as_current)
- Version management and lineage tracking
- Verification with reload

Prerequisites:
- MediaPlanPy SDK v3.0.0+ installed
- Workspace created (see examples_create_workspace.py)
- Media plans created (see examples_create_mediaplan.py)

How to Run:
1. First run examples_create_workspace.py to create a workspace
2. Then run examples_create_mediaplan.py to create media plans
3. Update WORKSPACE_ID and MEDIAPLAN_ID constants below, or provide when prompted
4. Open this file in your IDE
5. Run the entire script: python examples_edit_mediaplan.py
6. Or run individual functions by calling them from __main__

Next Steps After Running:
- Load edited plans to verify changes (examples_load_mediaplan.py)
- Export edited plans (examples_export_mediaplan.py)
- Query multiple plan versions (examples_list_objects.py)
- Configure custom fields with Dictionary (examples_12_manage_dictionary.py)
"""

import os
import json
from pathlib import Path
from datetime import date, datetime
from decimal import Decimal

from mediaplanpy.workspace import WorkspaceManager
from mediaplanpy.models import MediaPlan, TargetAudience, TargetLocation, MetricFormula


# ============================================================================
# USER CONFIGURATION
# Update these values after creating workspace and media plans
# ============================================================================

# Copy the "Workspace ID" from examples_create_workspace.py output
WORKSPACE_ID = "workspace_b92ee88b"

# Copy a "Media plan ID" from examples_create_mediaplan.py output
MEDIAPLAN_ID = "mediaplan_5cb7dc59"

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


def edit_minimal_plan(manager, plan):
    """
    Edit basic properties of a media plan and save with overwrite=True.

    Use Case:
        When you need to update basic properties like name, budget, or objective
        and want to overwrite the existing version rather than creating a new version.

    v3.0 Features:
        - Editing basic MediaPlan properties
        - Editing Campaign properties (budget, dates, objective)
        - save() with overwrite=True (preserves media plan ID)
        - Verification by reloading

    Args:
        manager: Loaded WorkspaceManager instance
        plan: Loaded MediaPlan instance

    Next Steps:
        - Reload the plan to verify changes were saved
        - Check that the media plan ID remains the same
        - Use overwrite=False to create new versions instead
    """
    print("\n" + "="*60)
    print("Editing Basic Properties with Overwrite")
    print("="*60)

    # Capture original values
    original_id = plan.meta.id
    original_name = plan.meta.name
    original_budget = plan.campaign.budget_total
    original_objective = plan.campaign.objective

    print(f"\nOriginal Values:")
    print(f"  - Media plan ID: {original_id}")
    print(f"  - Name: {original_name}")
    print(f"  - Campaign budget: ${original_budget:,.2f}")
    print(f"  - Campaign objective: {original_objective}")

    # Edit meta properties
    plan.meta.name = f"{original_name} (Updated {datetime.now().strftime('%Y-%m-%d %H:%M')})"
    plan.meta.comments = "Updated basic properties - budget and objective changes"

    # Edit campaign properties
    plan.campaign.budget_total = Decimal(str(float(original_budget) * 1.15))  # Increase by 15%
    plan.campaign.objective = "Brand Awareness and Consideration"

    print(f"\nNew Values:")
    print(f"  - Name: {plan.meta.name}")
    print(f"  - Comments: {plan.meta.comments}")
    print(f"  - Campaign budget: ${plan.campaign.budget_total:,.2f}")
    print(f"  - Campaign objective: {plan.campaign.objective}")

    # Save with overwrite=True (preserves media plan ID)
    print(f"\nSaving with overwrite=True (same media plan ID)...")
    saved_path = plan.save(manager, overwrite=True)
    print(f"✓ Saved to: {saved_path}")

    # Reload to verify changes
    print(f"\nReloading plan to verify changes...")
    reloaded_plan = MediaPlan.load(manager, media_plan_id=plan.meta.id)

    print(f"\nVerification:")
    print(f"  - Media plan ID unchanged: {reloaded_plan.meta.id == original_id}")
    print(f"  - Name updated: {reloaded_plan.meta.name == plan.meta.name}")
    print(f"  - Budget updated: ${reloaded_plan.campaign.budget_total:,.2f}")
    print(f"  - Objective updated: {reloaded_plan.campaign.objective}")

    print(f"\n✓ Basic properties edited and saved successfully")

    return reloaded_plan


def edit_complex_plan_with_v3_features(manager, plan):
    """
    Edit v3.0 features: target audiences, target locations, KPIs, line items, custom dimensions.

    Use Case:
        When you need to update v3.0 array-based models, add new objects to arrays,
        modify KPIs, update custom dimensions, edit line items, or merge custom_properties.

    v3.0 Features:
        - Modifying existing TargetAudience objects in array
        - Adding new TargetAudience objects to array
        - Modifying existing TargetLocation objects in array
        - Adding new TargetLocation objects to array
        - Updating KPI name/value pairs (kpi_name1-5, kpi_value1-5)
        - Updating custom dimensions (dim_custom1-5)
        - Merging custom_properties dictionaries
        - Proper LineItem CRUD pattern (load → edit → update)
        - Adding metric_formulas to line items
        - save() with overwrite=False (creates new version with parent_id)

    Args:
        manager: Loaded WorkspaceManager instance
        plan: Loaded MediaPlan instance

    Next Steps:
        - Reload to verify changes
        - Check that a new media plan ID was generated (overwrite=False)
        - Check that parent_id links to original plan
        - Query all versions for a campaign
    """
    print("\n" + "="*60)
    print("Editing v3.0 Features and Creating New Version")
    print("="*60)

    # Capture original values
    original_id = plan.meta.id
    original_audience_count = len(plan.campaign.target_audiences) if plan.campaign.target_audiences else 0
    original_location_count = len(plan.campaign.target_locations) if plan.campaign.target_locations else 0

    print(f"\nOriginal Values:")
    print(f"  - Media plan ID: {original_id}")
    print(f"  - Target audiences: {original_audience_count}")
    print(f"  - Target locations: {original_location_count}")
    print(f"  - Campaign KPI 1: {plan.campaign.kpi_name1 or '(not set)'}")
    print(f"  - Campaign dim_custom1: {plan.campaign.dim_custom1 or '(not set)'}")

    # ====================
    # 1. MODIFY EXISTING TARGET AUDIENCE
    # ====================
    print(f"\n1. Modifying existing target audience...")

    if plan.campaign.target_audiences and len(plan.campaign.target_audiences) > 0:
        # Modify first audience
        aud = plan.campaign.target_audiences[0]
        print(f"   - Original audience name: {aud.name}")

        aud.name = f"{aud.name} (Updated)"
        aud.description = "Updated audience with expanded age range"
        aud.demo_age_start = 25  # Expand age range
        aud.demo_age_end = 55
        aud.population_size = 5500000  # Update population

        print(f"   - Updated audience name: {aud.name}")
        print(f"   - Updated age range: {aud.demo_age_start}-{aud.demo_age_end}")
        print(f"   - Updated population: {aud.population_size:,.0f}")

    # ====================
    # 2. ADD NEW TARGET AUDIENCE
    # ====================
    print(f"\n2. Adding new target audience...")

    new_audience = TargetAudience(
        name="Millennials - Tech Enthusiasts",
        description="Young professionals interested in technology and innovation",
        demo_age_start=28,
        demo_age_end=42,
        demo_gender="Any",
        demo_attributes="Income: $80k+, Education: College+, Urban dwellers",
        interest_attributes="Technology, Innovation, Gadgets, Software, AI",
        intent_attributes="High purchase intent for tech products",
        purchase_attributes="Recent tech purchases, High online spending",
        extension_approach="Lookalike modeling based on seed audience",
        population_size=3200000
    )

    # Add to array
    if plan.campaign.target_audiences is None:
        plan.campaign.target_audiences = []
    plan.campaign.target_audiences.append(new_audience)

    print(f"   - Added audience: {new_audience.name}")
    print(f"   - Age range: {new_audience.demo_age_start}-{new_audience.demo_age_end}")
    print(f"   - Total audiences now: {len(plan.campaign.target_audiences)}")

    # ====================
    # 3. MODIFY EXISTING TARGET LOCATION
    # ====================
    print(f"\n3. Modifying existing target location...")

    if plan.campaign.target_locations and len(plan.campaign.target_locations) > 0:
        # Modify first location
        loc = plan.campaign.target_locations[0]
        print(f"   - Original location name: {loc.name}")

        loc.name = f"{loc.name} (Expanded)"
        loc.description = "Expanded to include additional markets"

        # If it has a location_list, add to it
        if loc.location_list:
            if isinstance(loc.location_list, list):
                loc.location_list.append("Texas")
                loc.location_list.append("Florida")
            else:
                # It might be a string, convert to list
                loc.location_list = [loc.location_list, "Texas", "Florida"]

        print(f"   - Updated location name: {loc.name}")

    # ====================
    # 4. ADD NEW TARGET LOCATION
    # ====================
    print(f"\n4. Adding new target location...")

    new_location = TargetLocation(
        name="West Coast Markets",
        description="Major metropolitan areas on the West Coast",
        location_type="State",
        location_list=["California", "Oregon", "Washington"],
        population_percent=Decimal("0.85")  # Targeting 85% of population
    )

    # Add to array
    if plan.campaign.target_locations is None:
        plan.campaign.target_locations = []
    plan.campaign.target_locations.append(new_location)

    print(f"   - Added location: {new_location.name}")
    print(f"   - Type: {new_location.location_type}")
    print(f"   - States: {', '.join(new_location.location_list) if isinstance(new_location.location_list, list) else new_location.location_list}")
    print(f"   - Total locations now: {len(plan.campaign.target_locations)}")

    # ====================
    # 5. UPDATE KPIs
    # ====================
    print(f"\n5. Updating campaign KPIs...")

    plan.campaign.kpi_name1 = "Brand Awareness Lift"
    plan.campaign.kpi_value1 = Decimal("15.5")  # 15.5% lift target

    plan.campaign.kpi_name2 = "Purchase Intent Increase"
    plan.campaign.kpi_value2 = Decimal("22.0")  # 22% increase target

    plan.campaign.kpi_name3 = "Website Traffic Growth"
    plan.campaign.kpi_value3 = Decimal("35000")  # 35k additional visits

    print(f"   - KPI 1: {plan.campaign.kpi_name1} = {plan.campaign.kpi_value1}")
    print(f"   - KPI 2: {plan.campaign.kpi_name2} = {plan.campaign.kpi_value2}")
    print(f"   - KPI 3: {plan.campaign.kpi_name3} = {plan.campaign.kpi_value3}")

    # ====================
    # 6. UPDATE CUSTOM DIMENSIONS
    # ====================
    print(f"\n6. Updating custom dimensions...")

    plan.campaign.dim_custom1 = "Tech Products Division"
    plan.campaign.dim_custom2 = "Q2 2025"

    # Update meta custom dimensions too
    plan.meta.dim_custom1 = "Strategic Initiative - Digital Transformation"

    print(f"   - Campaign dim_custom1: {plan.campaign.dim_custom1}")
    print(f"   - Campaign dim_custom2: {plan.campaign.dim_custom2}")
    print(f"   - Meta dim_custom1: {plan.meta.dim_custom1}")

    # ====================
    # 7. MERGE CUSTOM PROPERTIES
    # ====================
    print(f"\n7. Merging custom_properties...")

    # Add/merge campaign custom properties
    if plan.campaign.custom_properties is None:
        plan.campaign.custom_properties = {}

    plan.campaign.custom_properties.update({
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "updated_by": "Data Science Team",
        "optimization_status": "In Progress"
    })

    print(f"   - Campaign custom_properties keys: {', '.join(plan.campaign.custom_properties.keys())}")

    # ====================
    # 8. EDIT LINE ITEM USING PROPER CRUD PATTERN
    # ====================
    print(f"\n8. Editing line item using proper CRUD pattern...")

    if plan.lineitems and len(plan.lineitems) > 0:
        # PROPER PATTERN: Load → Edit → Update
        lineitem_id = plan.lineitems[0].id
        print(f"   - Loading line item by ID: {lineitem_id}")

        # Step 1: LOAD the line item
        li = plan.load_lineitem(lineitem_id)
        print(f"   - Loaded: {li.name}")

        # Step 2: EDIT the line item
        # Configure metric formulas using configure_metric_formula()
        # v3.0: Can now specify formula_type and base_metric to create
        # lineitem-level overrides that differ from dictionary defaults

        # Add a CTR formula for clicks using formula_type and base_metric parameters
        print(f"   - Configuring clicks formula with lineitem-level override...")
        li.configure_metric_formula(
            "metric_clicks",
            formula_type="conversion_rate",   # Create lineitem override
            base_metric="metric_impressions", # Must provide both parameters
            coefficient=Decimal("0.01"),      # CTR = 1%
            comments="Click-through rate calculation - lineitem override"
        )
        print(f"     ✓ Clicks: conversion_rate from impressions (CTR)")

        # Configure impressions with CPM using formula_type and base_metric parameters
        print(f"   - Configuring impressions formula with lineitem-level override...")
        li.configure_metric_formula(
            "metric_impressions",
            formula_type="cost_per_unit",    # Create lineitem override
            base_metric="cost_total",        # Must provide both parameters
            coefficient=Decimal("8.0"),      # CPM = $8.00
            comments="CPM calculation - lineitem override"
        )
        print(f"     ✓ Impressions: cost_per_unit from cost_total (CPM)")

        print(f"   - Formulas configured with lineitem-level overrides")
        print(f"     (These formulas are specific to this lineitem)")
        if li.metric_formulas:
            print(f"   - Total formulas: {len(li.metric_formulas)}")

        # Update line item custom properties
        if li.custom_properties is None:
            li.custom_properties = {}

        li.custom_properties.update({
            "optimization_round": "2",
            "performance_tier": "High"
        })

        print(f"   - Updated custom_properties")

        # Step 3: UPDATE the line item (with validation)
        print(f"   - Updating line item with validation...")
        plan.update_lineitem(li, validate=True)
        print(f"   ✓ Line item updated successfully")

    # ====================
    # 9. SAVE WITH NEW VERSION
    # ====================
    print(f"\n9. Saving as new version (overwrite=False)...")
    print(f"   - Original media plan ID: {original_id}")

    saved_path = plan.save(manager, overwrite=False, set_as_current=True)

    print(f"   - New media plan ID: {plan.meta.id}")
    print(f"   - Parent ID: {plan.meta.parent_id}")
    print(f"   - Is current: {plan.meta.is_current}")
    print(f"   - Saved to: {saved_path}")

    # ====================
    # 10. RELOAD TO VERIFY
    # ====================
    print(f"\n10. Reloading to verify changes...")

    reloaded_plan = MediaPlan.load(manager, media_plan_id=plan.meta.id)

    print(f"\nVerification:")
    print(f"  - New ID created: {reloaded_plan.meta.id != original_id}")
    print(f"  - Parent ID set: {reloaded_plan.meta.parent_id == original_id}")
    print(f"  - Target audiences: {len(reloaded_plan.campaign.target_audiences)}")
    print(f"  - Target locations: {len(reloaded_plan.campaign.target_locations)}")
    print(f"  - Campaign KPI 1: {reloaded_plan.campaign.kpi_name1} = {reloaded_plan.campaign.kpi_value1}")
    print(f"  - Campaign dim_custom1: {reloaded_plan.campaign.dim_custom1}")
    print(f"  - Is current version: {reloaded_plan.meta.is_current}")

    if reloaded_plan.lineitems and len(reloaded_plan.lineitems) > 0:
        li = reloaded_plan.lineitems[0]
        if li.metric_formulas:
            print(f"  - Line item formulas: {', '.join(li.metric_formulas.keys())}")

    print(f"\n✓ v3.0 features edited and saved as new version successfully")

    return reloaded_plan


def save_with_versioning_options(manager, plan):
    """
    Demonstrate advanced save() parameters for version management.

    Use Case:
        When you need fine-grained control over plan versioning:
        - Create new versions without setting them as current
        - Switch which version is current
        - Understand version lineage and history

    v3.0 Features:
        - save() with overwrite=False, set_as_current=True (new version, set as current)
        - save() with overwrite=False, set_as_current=False (new version, not current)
        - save() with overwrite=True (update same version)
        - is_current field for tracking current version
        - parent_id field for version lineage

    Args:
        manager: Loaded WorkspaceManager instance
        plan: Loaded MediaPlan instance

    Next Steps:
        - Query all versions for a campaign
        - Use set_as_current() to change which version is current
        - Archive old versions
        - Understand version history and lineage
    """
    print("\n" + "="*60)
    print("Advanced Save Options and Version Management")
    print("="*60)

    # Capture original state
    original_id = plan.meta.id
    original_name = plan.meta.name

    print(f"\nOriginal Plan:")
    print(f"  - Media plan ID: {original_id}")
    print(f"  - Name: {original_name}")
    print(f"  - Is current: {plan.meta.is_current if hasattr(plan.meta, 'is_current') else 'N/A'}")

    # ====================
    # SCENARIO 1: Create new version and set as current
    # ====================
    print(f"\n" + "-"*60)
    print("Scenario 1: Create New Version and Set as Current")
    print("-"*60)
    print("Parameters: overwrite=False, set_as_current=True")

    # Make a change
    plan.meta.name = f"{original_name} - Version 2"
    plan.campaign.budget_total = Decimal(str(float(plan.campaign.budget_total) * 1.10))

    print(f"\nChanges:")
    print(f"  - New name: {plan.meta.name}")
    print(f"  - New budget: ${plan.campaign.budget_total:,.2f}")

    # Save as new version, set as current
    print(f"\nSaving...")
    saved_path = plan.save(manager, overwrite=False, set_as_current=True)

    version2_id = plan.meta.id

    print(f"\nResult:")
    print(f"  - New media plan ID: {version2_id}")
    print(f"  - Parent ID: {plan.meta.parent_id}")
    print(f"  - Is current: {plan.meta.is_current}")
    print(f"  - Saved to: {saved_path}")

    # Verify by reloading
    reloaded_v2 = MediaPlan.load(manager, media_plan_id=version2_id)
    print(f"\nVerification (reload):")
    print(f"  - ID: {reloaded_v2.meta.id}")
    print(f"  - Is current: {reloaded_v2.meta.is_current}")

    # ====================
    # SCENARIO 2: Create new version WITHOUT setting as current
    # ====================
    print(f"\n" + "-"*60)
    print("Scenario 2: Create New Version WITHOUT Setting as Current")
    print("-"*60)
    print("Parameters: overwrite=False, set_as_current=False")

    # Make another change
    plan.meta.name = f"{original_name} - Version 3 (Experimental)"
    plan.campaign.budget_total = Decimal(str(float(plan.campaign.budget_total) * 1.05))

    print(f"\nChanges:")
    print(f"  - New name: {plan.meta.name}")
    print(f"  - New budget: ${plan.campaign.budget_total:,.2f}")

    # Save as new version, but NOT as current
    print(f"\nSaving...")
    saved_path = plan.save(manager, overwrite=False, set_as_current=False)

    version3_id = plan.meta.id

    print(f"\nResult:")
    print(f"  - New media plan ID: {version3_id}")
    print(f"  - Parent ID: {plan.meta.parent_id}")
    print(f"  - Is current: {plan.meta.is_current}")
    print(f"  - Saved to: {saved_path}")

    # Verify by reloading both versions
    reloaded_v3 = MediaPlan.load(manager, media_plan_id=version3_id)
    reloaded_v2_again = MediaPlan.load(manager, media_plan_id=version2_id)

    print(f"\nVerification (reload both versions):")
    print(f"  - Version 2 (ID: {version2_id}):")
    print(f"    - Is current: {reloaded_v2_again.meta.is_current}")
    print(f"  - Version 3 (ID: {version3_id}):")
    print(f"    - Is current: {reloaded_v3.meta.is_current}")
    print(f"\n  Note: Version 2 should still be current, Version 3 is experimental")

    # ====================
    # SCENARIO 3: Overwrite existing version
    # ====================
    print(f"\n" + "-"*60)
    print("Scenario 3: Overwrite Existing Version")
    print("-"*60)
    print("Parameters: overwrite=True")

    # Load version 3 and modify it
    plan_v3 = MediaPlan.load(manager, media_plan_id=version3_id)
    plan_v3.meta.comments = "Updated experimental version with additional notes"

    print(f"\nChanges:")
    print(f"  - Updated comments on Version 3")
    print(f"  - Current ID: {plan_v3.meta.id}")

    # Save with overwrite (keeps same ID)
    print(f"\nSaving with overwrite=True...")
    saved_path = plan_v3.save(manager, overwrite=True)

    print(f"\nResult:")
    print(f"  - Media plan ID (unchanged): {plan_v3.meta.id}")
    print(f"  - Same ID as before: {plan_v3.meta.id == version3_id}")
    print(f"  - Saved to: {saved_path}")

    # ====================
    # SUMMARY
    # ====================
    print(f"\n" + "="*60)
    print("Summary: Version Management Options")
    print("="*60)

    print(f"\nVersion Lineage:")
    print(f"  - Original (v1): {original_id}")
    print(f"  - Version 2:     {version2_id} (parent: {reloaded_v2_again.meta.parent_id}) - IS CURRENT")
    print(f"  - Version 3:     {version3_id} (parent: {reloaded_v3.meta.parent_id}) - Not current")

    print(f"\nKey Concepts:")
    print(f"  1. overwrite=False: Creates new version with new ID and parent_id")
    print(f"  2. overwrite=True:  Updates same version (keeps ID)")
    print(f"  3. set_as_current=True:  Marks version as current")
    print(f"  4. set_as_current=False: Marks version as NOT current")
    print(f"  5. set_as_current=None:  No change to is_current field")

    print(f"\nNext Steps:")
    print(f"  - Use WorkspaceManager.list_mediaplans() to see all versions")
    print(f"  - Filter by campaign_id to see versions of same campaign")
    print(f"  - Use parent_id to trace version lineage")
    print(f"  - Load specific versions by media_plan_id")

    print(f"\n✓ Version management demonstration completed successfully")


if __name__ == "__main__":
    print("="*60)
    print("MediaPlanPy v3.0 - Edit Media Plan Examples")
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

    print("\n=== Example 1: Edit Basic Properties with Overwrite ===")
    plan1 = edit_minimal_plan(manager, plan)

    print("\n=== Example 2: Edit v3.0 Features and Create New Version ===")
    # Reload the original plan for this example
    original_plan = MediaPlan.load(manager, media_plan_id=plan.meta.id)
    plan2 = edit_complex_plan_with_v3_features(manager, original_plan)

    print("\n=== Example 3: Advanced Save Options and Version Management ===")
    # Use the plan from example 2 (which has v3.0 features)
    save_with_versioning_options(manager, plan2)

    print("\n" + "="*60)
    print("Edit Media Plan Examples Completed!")
    print("="*60)

    print(f"\nWhat We Demonstrated:")
    print(f"  1. Edited basic properties (name, budget, objective)")
    print(f"  2. Modified v3.0 array-based models (target_audiences, target_locations)")
    print(f"  3. Added new objects to arrays")
    print(f"  4. Updated KPIs and custom dimensions")
    print(f"  5. Merged custom_properties dictionaries")
    print(f"  6. Proper LineItem CRUD pattern (load_lineitem → edit → update_lineitem)")
    print(f"  7. Configured lineitem-level formula overrides (formula_type, base_metric)")
    print(f"  8. Used overwrite=True to update existing versions")
    print(f"  9. Used overwrite=False to create new versions")
    print(f" 10. Used set_as_current to manage version state")
    print(f" 11. Verified changes by reloading")

    print(f"\nNext Steps:")
    print(f"  - Run examples_load_mediaplan.py to inspect edited plans")
    print(f"  - Run examples_export_mediaplan.py to export edited plans")
    print(f"  - Run examples_list_objects.py to query all versions")
    print(f"  - Run examples_12_manage_dictionary.py to configure custom fields")
