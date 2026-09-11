"""
MediaPlanPy Examples - Formula Management and Auto-Recalculation

This script demonstrates the v3.0 dynamic formula system through a progressive,
practical workflow. Starting with a simple media plan, we show how formulas enable
automatic recalculation and coefficient management.

Progressive Demonstration:
1. Create a simple media plan (2 line items, no formulas)
2. Edit costs → automatic recalculation of dependent metrics
3. Edit CPM → impressions recalculate from new coefficient
4. Edit clicks → CPC automatically updates
5. Configure dependency chain → cascading recalculation
6. Create lineitem-level formula overrides → 3-tier hierarchy

Prerequisites:
- MediaPlanPy SDK v3.0.0+ installed
- Workspace created (see examples_01_create_workspace.py)

How to Run:
1. Run examples_01_create_workspace.py first to create a workspace
2. Update WORKSPACE_ID constant at top of this file (or provide when prompted)
3. Run: python examples_15_formulas.py

Key Concepts:
- Default formulas: System uses cost_per_unit/cost_total if not specified
- Auto-recalculation: Changing base metrics recalculates dependents
- Bidirectional updates: Edit value→formula updates, or formula→value updates
- Dependency chains: Metrics can depend on other calculated metrics
"""

import os
from pathlib import Path
from datetime import date, datetime
from decimal import Decimal

from mediaplanpy.workspace import WorkspaceManager
from mediaplanpy.models import MediaPlan, Campaign, LineItem, Meta, Dictionary
from mediaplanpy.models.dictionary import MetricFormulaConfig
from mediaplanpy.models.metric_formula import MetricFormula


# ============================================================================
# USER CONFIGURATION
# Update these values after running examples_01_create_workspace.py
# ============================================================================

# Workspace ID for saving media plans
WORKSPACE_ID = "workspace_b92ee88b"

# ============================================================================


def get_configuration_value(config_name, prompt_message, example_value):
    """Get configuration value from constant or user input."""
    if config_name == 'WORKSPACE_ID':
        current_value = WORKSPACE_ID
    else:
        return None

    if "xxxxxxxx" not in current_value:
        return current_value

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

    return user_input if user_input else None


def load_workspace():
    """Load workspace for all examples."""
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
    print(f"✓ Workspace loaded successfully\n")

    return manager


def show_lineitem_state(lineitem, label=""):
    """Display current state of a line item."""
    if label:
        print(f"\n{label}:")

    print(f"  Cost Total:  ${float(lineitem.cost_total):>12,.2f}")

    if lineitem.metric_impressions:
        impr_obj = lineitem.get_metric_object("metric_impressions")
        formula_type = impr_obj.formula_type or "none"
        coef = float(impr_obj.coefficient) if impr_obj.coefficient else 0
        print(f"  Impressions: {int(lineitem.metric_impressions):>12,}  ({formula_type}, {coef:.4f})")

    if lineitem.metric_clicks:
        clicks_obj = lineitem.get_metric_object("metric_clicks")
        formula_type = clicks_obj.formula_type or "none"
        coef = float(clicks_obj.coefficient) if clicks_obj.coefficient else 0
        print(f"  Clicks:      {int(lineitem.metric_clicks):>12,}  ({formula_type}, {coef:.4f})")

    if lineitem.metric_conversions:
        conv_obj = lineitem.get_metric_object("metric_conversions")
        formula_type = conv_obj.formula_type or "none"
        coef = float(conv_obj.coefficient) if conv_obj.coefficient else 0
        print(f"  Conversions: {int(lineitem.metric_conversions):>12,}  ({formula_type}, {coef:.4f})")


def create_simple_mediaplan(manager):
    """
    Step 0: Create a simple media plan with two line items.

    Starting Point:
    - 2 line items with equal metrics
    - Direct value assignment (no formulas configured)
    - No dictionary configuration

    This demonstrates the baseline before formula system is activated.
    """
    print("=" * 70)
    print("STEP 0: Create Simple Media Plan")
    print("=" * 70)
    print("\nCreating media plan with 2 line items (equal metrics, no formulas)...")

    mediaplan = MediaPlan(
        meta=Meta(
            id="mp_formulas_demo",
            schema_version="v3.0",
            name="Formula Demo - Progressive Learning",
            created_by_name="Examples"
        ),
        campaign=Campaign(
            id="camp_001",
            name="Q1 2025 Campaign",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 3, 31),
            budget_total=Decimal("20000")
        ),
        lineitems=[
            LineItem(
                id="li_001",
                name="Display - Premium Sites",
                start_date=date(2025, 1, 1),
                end_date=date(2025, 3, 31),
                cost_total=Decimal("10000"),
                metric_impressions=Decimal("1000000"),
                metric_clicks=Decimal("25000"),
                metric_conversions=Decimal("2500")
                # Note: NO metric_formulas specified!
            ),
            LineItem(
                id="li_002",
                name="Display - Standard Sites",
                start_date=date(2025, 1, 1),
                end_date=date(2025, 3, 31),
                cost_total=Decimal("10000"),
                metric_impressions=Decimal("1000000"),
                metric_clicks=Decimal("25000"),
                metric_conversions=Decimal("2500")
                # Note: NO metric_formulas specified!
            )
        ]
    )

    print(f"\n✓ Media plan created: {mediaplan.meta.id}")

    show_lineitem_state(mediaplan.lineitems[0], "LineItem #1")
    show_lineitem_state(mediaplan.lineitems[1], "LineItem #2")

    print("\n" + "-" * 70)
    print("Summary:")
    print("  • Created 2 line items with equal metrics")
    print("  • No formulas configured yet")
    print("  • Ready to demonstrate formula system capabilities")

    # Save
    print("\nSaving to workspace...")
    mediaplan.save(manager)
    print("✓ Saved")

    return mediaplan


def step_01_edit_costs(manager, mediaplan):
    """
    Step 1: Edit cost_total on both line items → automatic recalculation.

    Demonstrates:
    - System uses default formula_type="cost_per_unit" and base_metric="cost_total"
    - Even without explicit formulas, dependent metrics recalculate automatically
    - Coefficients are preserved (CPM stays the same)

    Changes:
    - LineItem #1: Increase cost by 50% ($10k → $15k)
    - LineItem #2: Decrease cost by 50% ($10k → $5k)
    """
    print("\n\n" + "=" * 70)
    print("STEP 1: Edit Costs → Automatic Recalculation")
    print("=" * 70)
    print("\nDemonstrating: Default formulas enable automatic recalculation")
    print("Action: Increase LI#1 cost by 50%, decrease LI#2 cost by 50%")

    li1 = mediaplan.lineitems[0]
    li2 = mediaplan.lineitems[1]

    print("\nBEFORE:")
    show_lineitem_state(li1, "LineItem #1")
    show_lineitem_state(li2, "LineItem #2")

    # Edit costs using the new method
    print(f"\nChanging LineItem #1 cost: $10,000 → $15,000 (+50%)")
    recalc1 = li1.set_metric_value("cost_total", 15000)

    print(f"Changing LineItem #2 cost: $10,000 → $5,000 (-50%)")
    recalc2 = li2.set_metric_value("cost_total", 5000)

    print("\nAFTER:")
    show_lineitem_state(li1, "LineItem #1")
    show_lineitem_state(li2, "LineItem #2")

    print("\n" + "-" * 70)
    print("Summary:")
    print("  • Changed cost_total on both line items")
    print(f"  • LI#1 recalculated: {list(recalc1.keys())}")
    print(f"  • LI#2 recalculated: {list(recalc2.keys())}")
    print("  • System used default formulas (cost_per_unit from cost_total)")
    print("  • Coefficients preserved: CPM stayed at $10.00")
    print("  ✓ Dependent metrics automatically recalculated!")

    # Save
    print("\nSaving to workspace...")
    mediaplan.save(manager)
    print("✓ Saved")

    return mediaplan


def step_02_edit_cpm(manager, mediaplan):
    """
    Step 2: Edit CPM (formula parameter) → impressions recalculate.

    Demonstrates:
    - Editing formula parameters (coefficient) recalculates metric values
    - CPM ↓ 20% causes impressions ↑ 25% (inverse relationship)
    - Use configure_metric_formula() to update coefficients

    Changes:
    - LineItem #1: Decrease CPM from $10 to $8 (-20%)
    - Impressions increase from 1.5M to 1.875M (+25%)
    """
    print("\n\n" + "=" * 70)
    print("STEP 2: Edit CPM → Impressions Recalculate")
    print("=" * 70)
    print("\nDemonstrating: Formula parameters drive metric values")
    print("Action: Decrease CPM on LI#1 by 20% ($10 → $8)")

    li1 = mediaplan.lineitems[0]

    print("\nBEFORE:")
    show_lineitem_state(li1, "LineItem #1")

    # Get current CPM
    impr_obj = li1.get_metric_object("metric_impressions")
    old_cpm = float(impr_obj.cpm)
    old_impressions = li1.metric_impressions

    # Decrease CPM by 20%: $10 → $8 (coefficient: 0.010 → 0.008)
    print(f"\nConfiguring new CPM: ${old_cpm:.2f} → $8.00 (-20%)")
    recalc = li1.configure_metric_formula(
        "metric_impressions",
        coefficient=0.008,  # CPU for $8 CPM
        comments="Negotiated lower CPM"
    )

    print("\nAFTER:")
    show_lineitem_state(li1, "LineItem #1")

    new_impressions = li1.metric_impressions
    change_pct = ((new_impressions / old_impressions) - 1) * 100

    print("\n" + "-" * 70)
    print("Summary:")
    print(f"  • Changed CPM: ${old_cpm:.2f} → $8.00 (↓20%)")
    print(f"  • Impressions: {int(old_impressions):,} → {int(new_impressions):,} (↑{change_pct:.1f}%)")
    print(f"  • Recalculated metrics: {list(recalc.keys())}")
    print("  ✓ Lower CPM = More impressions for same cost!")

    # Save
    print("\nSaving to workspace...")
    mediaplan.save(manager)
    print("✓ Saved")

    return mediaplan


def step_03_edit_clicks(manager, mediaplan):
    """
    Step 3: Edit clicks value → CPC automatically updates.

    Demonstrates:
    - Editing metric values automatically updates formula coefficients
    - Clicks ↑ 50% causes CPC ↓ 33% (inverse relationship)
    - Use set_metric_value() with update_coefficient=True (default)

    Changes:
    - LineItem #2: Increase clicks from 12,500 to 18,750 (+50%)
    - CPC decreases from $0.40 to $0.267 (-33%)
    """
    print("\n\n" + "=" * 70)
    print("STEP 3: Edit Clicks → CPC Automatically Updates")
    print("=" * 70)
    print("\nDemonstrating: Metric values update formula coefficients")
    print("Action: Increase clicks on LI#2 by 50%")

    li2 = mediaplan.lineitems[1]

    print("\nBEFORE:")
    show_lineitem_state(li2, "LineItem #2")

    # Get current values
    clicks_obj = li2.get_metric_object("metric_clicks")
    old_clicks = li2.metric_clicks
    old_cpc = float(clicks_obj.coefficient)

    # Increase clicks by 50%
    new_clicks = old_clicks * Decimal("1.5")
    print(f"\nSetting clicks: {int(old_clicks):,} → {int(new_clicks):,} (+50%)")
    recalc = li2.set_metric_value("metric_clicks", new_clicks)

    print("\nAFTER:")
    show_lineitem_state(li2, "LineItem #2")

    clicks_obj = li2.get_metric_object("metric_clicks")
    new_cpc = float(clicks_obj.coefficient)
    cpc_change_pct = ((new_cpc / old_cpc) - 1) * 100

    print("\n" + "-" * 70)
    print("Summary:")
    print(f"  • Changed clicks: {int(old_clicks):,} → {int(new_clicks):,} (↑50%)")
    print(f"  • CPC: ${old_cpc:.3f} → ${new_cpc:.3f} ({cpc_change_pct:+.1f}%)")
    print("  • Coefficient automatically recalculated")
    print("  ✓ More clicks for same cost = Lower CPC!")

    # Save
    print("\nSaving to workspace...")
    mediaplan.save(manager)
    print("✓ Saved")

    return mediaplan


def step_04_configure_dependencies(manager, mediaplan):
    """
    Step 4: Configure dependency chain → cascading recalculation.

    Demonstrates:
    - Setting up metric dependencies at dictionary level
    - Changing formula types (cost_per_unit → conversion_rate)
    - Cascading recalculation through dependency chain
    - Coefficient preservation during formula type changes

    Configuration:
    - cost_total → impressions (cost_per_unit)
    - impressions → clicks (conversion_rate)
    - clicks → conversions (conversion_rate)

    Then demonstrate:
    - Change CPM on LI#1 → impressions, clicks, conversions all recalculate
    """
    print("\n\n" + "=" * 70)
    print("STEP 4: Configure Dependencies → Cascading Recalculation")
    print("=" * 70)
    print("\nDemonstrating: Full dependency chain with cascading updates")
    print("Configuration: cost_total → impressions → clicks → conversions")

    li1 = mediaplan.lineitems[0]
    li2 = mediaplan.lineitems[1]

    print("\nBEFORE (current formula types):")
    print("  • impressions: cost_per_unit (from cost_total)")
    print("  • clicks:      cost_per_unit (from cost_total)")
    print("  • conversions: cost_per_unit (from cost_total)")

    show_lineitem_state(li1, "\nLineItem #1 - Current State")
    show_lineitem_state(li2, "LineItem #2 - Current State")

    # Configure dependency chain
    print("\n" + "-" * 70)
    print("Configuring dependency chain...")

    print("\n1. Setting clicks formula: conversion_rate from metric_impressions")
    result1 = mediaplan.select_metric_formula(
        "metric_clicks",
        formula_type="conversion_rate",
        base_metric="metric_impressions"
    )
    print(f"   ✓ Updated {result1['lineitems_updated']} lineitems, "
          f"recalculated {result1['coefficients_recalculated']} coefficients")

    print("\n2. Setting conversions formula: conversion_rate from metric_clicks")
    result2 = mediaplan.select_metric_formula(
        "metric_conversions",
        formula_type="conversion_rate",
        base_metric="metric_clicks"
    )
    print(f"   ✓ Updated {result2['lineitems_updated']} lineitems, "
          f"recalculated {result2['coefficients_recalculated']} coefficients")

    print("\nAFTER (new formula types):")
    print("  • impressions: cost_per_unit (from cost_total)")
    print("  • clicks:      conversion_rate (from metric_impressions) ← Changed!")
    print("  • conversions: conversion_rate (from metric_clicks) ← Changed!")

    show_lineitem_state(li1, "\nLineItem #1 - After Configuration")
    show_lineitem_state(li2, "LineItem #2 - After Configuration")

    print("\n" + "-" * 70)
    print("Summary of configuration:")
    print("  • Clicks now calculated from impressions (CTR-based)")
    print("  • Conversions calculated from clicks (CVR-based)")
    print("  • Values preserved by reverse-calculating coefficients")
    print("  ✓ Dependency chain established!")

    # Save
    print("\nSaving to workspace...")
    mediaplan.save(manager)
    print("✓ Saved")

    # Now demonstrate cascading recalculation
    print("\n" + "=" * 70)
    print("Demonstrating Cascading Recalculation")
    print("=" * 70)
    print("\nAction: Change CPM on LI#1, watch the cascade!")

    print("\nBEFORE:")
    show_lineitem_state(li1, "LineItem #1")

    # Save values for comparison
    old_impr = li1.metric_impressions
    old_clicks = li1.metric_clicks
    old_conv = li1.metric_conversions

    # Change CPM: $8 → $6.40 (-20%)
    print(f"\nConfiguring new CPM: $8.00 → $6.40 (-20%)")
    recalc = li1.configure_metric_formula(
        "metric_impressions",
        coefficient=Decimal("0.0064"),  # CPU for $6.40 CPM
        comments="Further negotiated CPM"
    )

    print("\nAFTER:")
    show_lineitem_state(li1, "LineItem #1")

    # Calculate changes
    impr_change = ((li1.metric_impressions / old_impr) - 1) * 100
    clicks_change = ((li1.metric_clicks / old_clicks) - 1) * 100 if old_clicks else 0
    conv_change = ((li1.metric_conversions / old_conv) - 1) * 100 if old_conv else 0

    print("\n" + "-" * 70)
    print("Summary of cascading changes:")
    print(f"  • Changed CPM: $8.00 → $6.40 (↓20%)")
    print(f"  • Impressions: {int(old_impr):,} → {int(li1.metric_impressions):,} ({impr_change:+.1f}%)")
    print(f"  • Clicks:      {int(old_clicks):,} → {int(li1.metric_clicks):,} ({clicks_change:+.1f}%)")
    print(f"  • Conversions: {int(old_conv):,} → {int(li1.metric_conversions):,} ({conv_change:+.1f}%)")
    print(f"  • Recalculated: {list(recalc.keys())}")
    print("  ✓ One change cascaded through entire dependency chain!")

    # Save final state
    print("\nSaving final state to workspace...")
    mediaplan.save(manager)
    print("✓ Saved")

    return mediaplan


def step_05_lineitem_overrides(manager, mediaplan):
    """
    Step 5: Create lineitem-level formula overrides.

    Demonstrates the 3-tier formula hierarchy in v3.0:
    1. Lineitem-level override (highest priority)
    2. Dictionary-level definition (fallback)
    3. Defaults (ultimate fallback)

    Use Case:
    - Different lineitems need different formulas for the same metric
    - Example: Premium placement uses CPM pricing, standard uses CPM+CTR hybrid

    Configuration:
    - LineItem #1: clicks from impressions (CTR) - uses dictionary definition
    - LineItem #2: clicks from cost (CPC) - lineitem override!

    This allows flexible per-lineitem formula configuration while maintaining
    plan-level defaults for consistency.
    """
    print("\n\n" + "=" * 70)
    print("STEP 5: Lineitem-Level Formula Overrides")
    print("=" * 70)
    print("\nDemonstrating: 3-Tier Formula Hierarchy (v3.0)")
    print("  • Tier 1: Lineitem override (highest priority)")
    print("  • Tier 2: Dictionary definition (fallback)")
    print("  • Tier 3: Defaults (ultimate fallback)")

    li1 = mediaplan.lineitems[0]
    li2 = mediaplan.lineitems[1]

    print("\n" + "-" * 70)
    print("Current Configuration:")
    print("  • Both lineitems use dictionary formula for clicks")

    # Check current formula definitions using the hierarchy method
    li1_formula = li1.get_metric_formula_definition("metric_clicks")
    li2_formula = li2.get_metric_formula_definition("metric_clicks")

    print(f"\n  LI#1 clicks: {li1_formula['formula_type']} from {li1_formula['base_metric']}")
    print(f"  LI#2 clicks: {li2_formula['formula_type']} from {li2_formula['base_metric']}")

    print("\nBEFORE (both use same formula):")
    show_lineitem_state(li1, "LineItem #1 - Premium Placement")
    show_lineitem_state(li2, "LineItem #2 - Standard Placement")

    # Create lineitem-level override for LI#2
    print("\n" + "-" * 70)
    print("Creating Lineitem Override for LI#2...")
    print("\nScenario: Standard placement negotiated CPC pricing")
    print("  • LI#2 will use CPC (cost_per_unit from cost_total)")
    print("  • LI#1 continues using CTR (dictionary definition)")

    print("\nConfiguring lineitem override with formula_type and base_metric...")
    recalc = li2.configure_metric_formula(
        "metric_clicks",
        formula_type="cost_per_unit",     # Override: Use CPC instead of CTR
        base_metric="cost_total",         # Must provide both parameters
        coefficient=Decimal("0.267"),     # CPC = $0.267 (calculated from current values)
        comments="Standard placement uses CPC pricing model"
    )

    print("\nAFTER (different formulas per lineitem):")
    show_lineitem_state(li1, "LineItem #1 - Premium (CTR from dictionary)")
    show_lineitem_state(li2, "LineItem #2 - Standard (CPC override)")

    # Verify the hierarchy is working
    li1_formula_after = li1.get_metric_formula_definition("metric_clicks")
    li2_formula_after = li2.get_metric_formula_definition("metric_clicks")

    print("\n" + "-" * 70)
    print("Verification using get_metric_formula_definition():")
    print(f"  • LI#1: {li1_formula_after['formula_type']} from {li1_formula_after['base_metric']}")
    print(f"    → Uses dictionary definition (Tier 2)")
    print(f"  • LI#2: {li2_formula_after['formula_type']} from {li2_formula_after['base_metric']}")
    print(f"    → Uses lineitem override (Tier 1) ✓")

    # Demonstrate the difference with a practical example
    print("\n" + "-" * 70)
    print("Practical Impact: Change cost on both lineitems")
    print("\nBoth lineitems have $5,000 budget. Increase to $6,000 (+20%):")

    old_li1_clicks = li1.metric_clicks
    old_li2_clicks = li2.metric_clicks

    print("\nChanging both costs to $6,000...")
    li1.set_metric_value("cost_total", 6000)
    li2.set_metric_value("cost_total", 6000)

    print("\nResult:")
    print(f"  • LI#1 clicks: {int(old_li1_clicks):,} → {int(li1.metric_clicks):,}")
    print(f"    Uses CTR - clicks recalculated from impressions")
    print(f"  • LI#2 clicks: {int(old_li2_clicks):,} → {int(li2.metric_clicks):,}")
    print(f"    Uses CPC - clicks recalculated from cost (+20%)")

    li1_change = ((li1.metric_clicks / old_li1_clicks) - 1) * 100 if old_li1_clicks else 0
    li2_change = ((li2.metric_clicks / old_li2_clicks) - 1) * 100 if old_li2_clicks else 0

    print(f"\n  • LI#1 click change: {li1_change:+.1f}% (CTR-based: depends on impressions)")
    print(f"  • LI#2 click change: {li2_change:+.1f}% (CPC-based: proportional to cost)")

    print("\n" + "-" * 70)
    print("Summary:")
    print("  ✓ Same metric (clicks) uses different formulas on different lineitems")
    print("  ✓ LI#1 uses dictionary definition (Tier 2 - fallback)")
    print("  ✓ LI#2 uses lineitem override (Tier 1 - highest priority)")
    print("  ✓ Both lineitems respond differently to cost changes")
    print("  ✓ Enables flexible pricing models within same media plan!")

    print("\nKey Concept: 3-Tier Hierarchy")
    print("  1. Check lineitem's metric_formulas for override")
    print("  2. If not found, check dictionary definition")
    print("  3. If not found, use system defaults")
    print("  → This hierarchy is queried via get_metric_formula_definition()")

    # Save final state
    print("\nSaving final state to workspace...")
    mediaplan.save(manager)
    print("✓ Saved")

    return mediaplan


# ============================================================================
# Main Execution
# ============================================================================

def main():
    """
    Run all formula examples in sequence.

    This progressive demonstration shows how the formula system works,
    from simple value assignment to complex dependency chains with
    automatic cascading recalculation.
    """
    print("=" * 70)
    print("MediaPlanPy v3.0 - Formula System Progressive Demonstration")
    print("=" * 70)
    print("\nThis example demonstrates:")
    print("  • Automatic recalculation with default formulas")
    print("  • Editing formulas to change metric values")
    print("  • Editing values to update formula coefficients")
    print("  • Configuring dependency chains for cascading updates")
    print("  • Lineitem-level formula overrides (3-tier hierarchy)")

    # Load workspace
    manager = load_workspace()
    if manager is None:
        print("\n❌ Cannot proceed without workspace")
        return

    # Execute progressive demonstration
    try:
        # Step 0: Create baseline
        mediaplan = create_simple_mediaplan(manager)

        # Step 1: Edit costs → auto-recalculation
        mediaplan = step_01_edit_costs(manager, mediaplan)

        # Step 2: Edit CPM → impressions change
        mediaplan = step_02_edit_cpm(manager, mediaplan)

        # Step 3: Edit clicks → CPC updates
        mediaplan = step_03_edit_clicks(manager, mediaplan)

        # Step 4: Configure dependencies → cascading
        mediaplan = step_04_configure_dependencies(manager, mediaplan)

        # Step 5: Lineitem-level formula overrides
        mediaplan = step_05_lineitem_overrides(manager, mediaplan)

        print("\n\n" + "=" * 70)
        print("✓ All Steps Completed Successfully!")
        print("=" * 70)
        print(f"\nYour media plan: {mediaplan.meta.id}")
        print(f"Workspace: {manager.config['workspace_id']}")
        print("\nWhat you learned:")
        print("  1. Default formulas enable automatic recalculation")
        print("  2. Edit formula parameters → metric values recalculate")
        print("  3. Edit metric values → formula coefficients update")
        print("  4. Dependency chains → changes cascade automatically")
        print("  5. Lineitem overrides → 3-tier hierarchy (lineitem → dictionary → defaults)")
        print("\nNext Steps:")
        print("  • Inspect JSON files in workspace to see formula configuration")
        print("  • Try examples_04_load_mediaplan.py to reload and continue editing")
        print("  • Explore examples_06_export_mediaplan.py to export to Excel")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
