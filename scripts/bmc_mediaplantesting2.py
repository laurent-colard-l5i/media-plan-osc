"""
MediaPlanPy Examples - Create Media Plan

This script demonstrates how to create media plans using MediaPlanPy SDK v3.0.
Examples progress from minimal to advanced, showcasing all v3.0 features.

v3.0 Features Demonstrated:
- MediaPlan.create() API with v3.0 schema
- target_audiences arrays (TargetAudience objects)
- target_locations arrays (TargetLocation objects)
- KPIs (kpi_name1-5, kpi_value1-5)
- Custom dimensions (dim_custom1-5 at all levels)
- custom_properties dictionaries (extensibility)
- metric_formulas (MetricFormula objects)
- Dictionary configuration (custom field captions and formulas)
- Enhanced metrics (reach, views, engagement)
- Enhanced costs (min/max, exchange rates, custom1-10)
- Buy information (buy_type, buy_commitment)

Prerequisites:
- MediaPlanPy SDK v3.0.0+ installed
- Workspace created (see examples_create_workspace.py)

How to Run:
1. Run examples_create_workspace.py first to create a workspace
2. Update WORKSPACE_ID constant at top of this file (or provide when prompted)
3. Open this file in your IDE
4. Run the entire script: python examples_create_mediaplan.py
5. Or run individual functions by calling them from __main__

Next Steps After Running:
- Load created media plans (see examples_load_mediaplan.py)
- Edit media plans (see examples_edit_mediaplan.py)
- Export to JSON/Excel (see examples_export_mediaplan.py)
"""

import os
from pathlib import Path
from datetime import date, datetime
from decimal import Decimal

from mediaplanpy.workspace import WorkspaceManager
from mediaplanpy.models import MediaPlan


# ============================================================================
# USER CONFIGURATION
# Update these values after running examples_create_workspace.py
# ============================================================================

# Workspace ID for saving media plans
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
    print(f"  1. Enter the value now (paste from examples_create_workspace.py output)")
    print(f"  2. Type 'skip' to skip all examples")
    print(f"  3. Update the constant at the top of this file and re-run")

    user_input = input(f"\n{prompt_message}: ").strip()

    if user_input.lower() == 'skip':
        print("Skipping all examples.")
        return None

    if user_input:
        return user_input
    else:
        print("No value provided. Skipping all examples.")
        return None


def load_workspace():
    """
    Load workspace once for use across all examples.

    Returns:
        WorkspaceManager instance or None if user skips
    """
    # Get workspace ID (prompt once)
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


def create_minimal_hello_world_plan(manager):
    """
    Create the simplest possible v3.0 media plan with only required fields.

    Use Case:
        Starting point for beginners - demonstrates minimum requirements
        for a valid v3.0 media plan with one campaign and one line item.

    v3.0 Features:
        - Schema version 3.0 enforcement
        - Required meta fields (id, name, created_by)
        - Required campaign fields (name, budget)
        - Required lineitem fields (name, channel, adformat)
        - Basic save operation

    Args:
        manager: Loaded WorkspaceManager instance

    Returns:
        MediaPlan object

    Next Steps:
        - Load the created plan (examples_load_mediaplan.py)
        - Add more line items
        - Add v3.0 features (audiences, locations, KPIs)
    """
    print("\n" + "="*60)
    print("Creating Minimal Hello World Media Plan")
    print("="*60)
    print(f"\nCreating minimal media plan...")

    # Create the simplest possible media plan
    plan = MediaPlan.create(
        # Required parameters
        campaign_name="BMc First Campaign",
        campaign_start_date="2025-01-01",
        campaign_end_date="2025-03-31",
        campaign_budget_total=Decimal("20000.00"),
        created_by_name="Brian McManus",

        # Optional: Media plan name (uses campaign_name if not provided)
        media_plan_name="Hello World Media Plan",

        # Optional: Line items (can also add later with create_lineitem())
        lineitems=[
            {
                "name": "Line Item 1",
                "cost_total": Decimal("5000.00")
            }
        ]
    )

    print(f"\n✓ Media plan created successfully")
    print(f"\nMedia Plan Details:")
    print(f"  - ID: {plan.meta.id}")
    print(f"  - Name: {plan.meta.name}")
    print(f"  - Schema version: {plan.meta.schema_version}")
    print(f"  - Campaign: {plan.campaign.name}")
    print(f"  - Budget: ${plan.campaign.budget_total:,.2f}")
    print(f"  - Line items: {len(plan.lineitems)}")

    # Save the media plan
    print(f"\nSaving media plan to workspace...")
    saved_path = plan.save(manager)

    print(f"\n✓ Media plan saved successfully")
    print(f"\nSaved to:")
    print(f"  - Primary file (JSON): {saved_path}")
    print(f"  - Analytics file (Parquet): {saved_path.replace('.json', '.parquet')}")

    # Check if database is enabled
    db_enabled = manager.config.get('database', {}).get('enabled', False)
    if db_enabled:
        db_table = manager.config['database'].get('table_name', 'media_plans')
        print(f"  - Database: Inserted into table '{db_table}'")
    else:
        print(f"  - Database: Not configured (file-based storage only)")

    print(f"\nStorage Details:")
    print(f"  - Workspace: {manager.config.get('workspace_id', 'N/A')}")
    print(f"  - Media plan ID: {plan.meta.id}")
    print(f"  - Format: JSON (human-readable) + Parquet (analytics-optimized)")

    print(f"\nNext Steps:")
    print(f"  1. Run examples_load_mediaplan.py to load this plan")
    print(f"  2. Run examples_edit_mediaplan.py to edit this plan")
    print(f"  3. Try create_complex_plan_with_loops() for more line items")

    return plan


def create_complex_plan_with_loops(manager):
    """
    Create a complex media plan with multiple line items generated programmatically.

    Use Case:
        Demonstrates how to efficiently create media plans with many line items
        using loops and list comprehensions.Useful for large campaigns with
        repeated structures (e.g., multiple ad formats across channels).

    v3.0 Features:
        - Programmatic line item generation
        - Multiple channels and ad formats
        - Date ranges and budget allocation
        - Cost calculations across line items

    Args:
        manager: Loaded WorkspaceManager instance

    Returns:
        MediaPlan object

    Next Steps:
        - Query line items by channel (examples_list_objects.py)
        - Aggregate costs by channel (examples_sql_queries.py)
        - Export to Excel for review (examples_export_mediaplan.py)
    """
    print("\n" + "="*60)
    print("Creating Complex Media Plan with Loops")
    print("="*60)
    print(f"\nCreating complex media plan with multiple line items...")

    # Define channels and ad formats to generate line items for
    channels_adformats = [
        {"channel": "Digital", "adformats": ["Banner", "Video", "Native"]},
        {"channel": "Social", "adformats": ["Feed", "Stories", "Reels"]},
        {"channel": "Search", "adformats": ["Brand", "Generic", "Product"]},
        {"channel": "Display", "adformats": ["Programmatic", "Direct", "Retargeting"]}
    ]

    # Generate line items programmatically
    lineitems = []
    total_budget = Decimal("100000.00")
    num_items = sum(len(cp["adformats"]) for cp in channels_adformats)
    budget_per_item = total_budget / num_items

    item_counter = 1
    for channel_config in channels_adformats:
        channel = channel_config["channel"]
        for adformat in channel_config["adformats"]:
            lineitems.append({
                "name": f"{channel} - {adformat}",
                "channel": channel,
                "adformat": adformat,
                "cost_total": budget_per_item,
                "metric_impressions": 100000 * item_counter,
                "metric_clicks": 2000 * item_counter,
                "start_date": "2025-01-01",
                "end_date": "2025-03-31"
            })
            item_counter += 1

    # Create the media plan
    plan = MediaPlan.create(
        # Required parameters
        campaign_name="Q1 2025 Multi-Channel Campaign",
        campaign_start_date="2025-01-01",
        campaign_end_date="2025-03-31",
        campaign_budget_total=total_budget,
        created_by_name="examples_user",

        # Campaign details
        campaign_objective="awareness",
        media_plan_name="Q1 2025 Complex Media Plan",

        # Programmatically generated line items
        lineitems=lineitems
    )

    print(f"\n✓ Media plan created successfully")
    print(f"\nMedia Plan Details:")
    print(f"  - ID: {plan.meta.id}")
    print(f"  - Name: {plan.meta.name}")
    print(f"  - Campaign: {plan.campaign.name}")
    print(f"  - Budget: ${plan.campaign.budget_total:,.2f}")
    print(f"  - Duration: {plan.campaign.start_date} to {plan.campaign.end_date}")
    print(f"  - Line items: {len(plan.lineitems)}")

    # Show line item breakdown by channel
    print(f"\nLine Items by Channel:")
    for channel_config in channels_adformats:
        channel = channel_config["channel"]
        channel_items = [li for li in plan.lineitems if li.channel == channel]
        channel_cost = sum(li.cost_total for li in channel_items)
        print(f"  - {channel}: {len(channel_items)} items, ${channel_cost:,.2f}")

    # Save the media plan
    print(f"\nSaving media plan to workspace...")
    saved_path = plan.save(manager)

    print(f"\n✓ Media plan saved successfully")
    print(f"\nSaved to:")
    print(f"  - Primary file (JSON): {saved_path}")
    print(f"  - Analytics file (Parquet): {saved_path.replace('.json', '.parquet')}")

    # Check if database is enabled
    db_enabled = manager.config.get('database', {}).get('enabled', False)
    if db_enabled:
        db_table = manager.config['database'].get('table_name', 'media_plans')
        print(f"  - Database: Inserted into table '{db_table}'")

    print(f"\nNext Steps:")
    print(f"  1. Run examples_list_objects.py to query line items")
    print(f"  2. Run examples_sql_queries.py for channel analysis")
    print(f"  3. Run examples_export_mediaplan.py to export to Excel")

    return plan


def create_advanced_plan_with_v3_features(manager):
    """
    Create an advanced media plan showcasing ALL v3.0 features.

    Use Case:
        Comprehensive demonstration of every v3.0 feature including audiences,
        locations, KPIs, custom dimensions, metric formulas, and Dictionary configuration.
        This is the complete reference example for v3.0 capabilities.

    v3.0 Features (COMPREHENSIVE):
        - target_audiences array (multiple audiences with 13+ attributes)
        - target_locations array (multiple locations with geographic targeting)
        - KPIs (kpi_name1-5, kpi_value1-5) for performance tracking
        - Custom dimensions (dim_custom1-5) at meta, campaign, and lineitem levels
        - custom_properties dictionaries for extensibility
        - metric_formulas (MetricFormula objects) for calculated metrics
        - Dictionary configuration (custom field captions and formulas)
        - Enhanced metrics (reach, views, engagement)
        - Enhanced costs (minimum, maximum, exchange rates)
        - Custom costs (cost_custom1-10) and custom metrics (metric_custom1-10)
        - Buy information (buy_type, buy_commitment)

    Args:
        manager: Loaded WorkspaceManager instance

    Returns:
        MediaPlan object

    Next Steps:
        - Inspect all v3.0 fields (examples_load_mediaplan.py)
        - Edit arrays and nested objects (examples_edit_mediaplan.py)
        - Query by custom dimensions (examples_sql_queries.py)
    """
    print("\n" + "="*60)
    print("Creating Advanced Media Plan with ALL v3.0 Features")
    print("="*60)
    print(f"\nCreating advanced media plan with all v3.0 features...")

    # === TARGET AUDIENCES (v3.0 Array Feature) ===
    target_audiences = [
        {
            "name": "Tech-Savvy Millennials",
            "description": "Young professionals interested in technology and innovation",
            "demo_age_start": 25,
            "demo_age_end": 40,
            "demo_gender": "Any",
            "demo_attributes": "Income: $75k+, Education: College+, Urban",
            "interest_attributes": "Technology, Innovation, Startups, AI, Cloud Computing",
            "extension_approach": "lookalike",
            "population_size": 2500000
        },
        {
            "name": "Business Decision Makers",
            "description": "C-level executives and senior managers",
            "demo_age_start": 35,
            "demo_age_end": 65,
            "demo_gender": "Any",
            "demo_attributes": "Income: $150k+, Job Title: C-Level, VP, Director",
            "population_size": 800000
        }
    ]

    # === TARGET LOCATIONS (v3.0 Array Feature) ===
    target_locations = [
        {
            "name": "Major US Metro Areas",
            "description": "Top 5 US metropolitan markets",
            "location_type": "DMA",
            "location_list": ["New York", "Los Angeles", "Chicago", "San Francisco", "Boston"],
            "population_percent": 0.35  # 35% of total audience
        },
        {
            "name": "Tech Hub Cities",
            "description": "Cities with high concentration of tech companies",
            "location_type": "DMA",
            "location_list": ["Seattle", "Austin", "Denver", "Portland"],
            "exclusion_list": ["Rural areas"],
            "population_percent": 0.15  # 15% of total audience
        },
        {
            "name": "National Coverage",
            "description": "Nationwide reach with urban focus",
            "location_type": "Country",
            "location_list": ["United States"],
            "exclusion_type": "State",
            "exclusion_list": ["Alaska", "Hawaii"],  # Example exclusions
            "population_percent": 0.95  # 50% of total audience
        }
    ]

    # === LINE ITEMS WITH ADVANCED v3.0 FEATURES ===
    lineitems = [
        {
            "name": "Digital Display - Programmatic",
            "channel": "Digital",
            "adformat": "Programmatic Display",
            "start_date": "2025-01-01",
            "end_date": "2025-03-31",

            # Costs (v3.0 enhancements)
            "cost_total": Decimal("50000.00"),
            "cost_minimum": Decimal("45000.00"),
            "cost_maximum": Decimal("55000.00"),
            "cost_currency": "USD",
            "cost_currency_exchange_rate": Decimal("1.0"),
            "cost_custom1": Decimal("2500.00"),  # Example: Agency fees

            # Metrics (v3.0 enhancements)
            "metric_impressions": 5000000,
            "metric_clicks": 100000,
            "metric_reach": 2000000,
            "metric_view_starts": 3000000,
            "metric_view_completions": 2400000,
            "metric_engagements": 150000,
            "metric_custom1": 85000,  # Example: Video views at 50%

            # Buy information (v3.0)
            "buy_type": "Programmatic",
            "buy_commitment": "Non-guaranteed",

            # Custom dimensions (v3.0)
            "dim_custom1": "Audience: Tech Millennials",

            # Metric formulas (v3.0) - will be added after line item creation
            "metric_formulas": {
                "metric_clicks": {
                    "formula_type": "conversion_rate",
                    "base_metric": "metric_impressions",
                    "coefficient": 0.01
                }
            },

            # Custom properties (v3.0 extensibility)
            "custom_properties": {
                "creative_type": "video",
                "optimization_goal": "reach",
                "bidding_strategy": "CPM",
                "targeting_expansion": True
            }
        },
        {
            "name": "Social Media - Feed Ads",
            "channel": "Social",
            "adformat": "Feed Ads",
            "start_date": "2025-01-01",
            "end_date": "2025-03-31",

            # Costs
            "cost_total": Decimal("30000.00"),
            "cost_minimum": Decimal("28000.00"),
            "cost_maximum": Decimal("32000.00"),

            # Metrics
            "metric_impressions": 8000000,
            "metric_clicks": 160000,
            "metric_reach": 3000000,
            "metric_engagements": 400000,

            # Buy information
            "buy_type": "Direct",
            "buy_commitment": "Guaranteed",

            # Custom dimensions
            "dim_custom1": "Audience: Business Leaders",

            # Metric formulas
            "metric_formulas": {
                "metric_clicks": {
                    "formula_type": "conversion_rate",
                    "base_metric": "metric_impressions",
                    "coefficient": 0.01
                }
            },

            # Custom properties
            "custom_properties": {
                "platform": "linkedin",
                "ad_format": "sponsored_content",
                "targeting_method": "account_based"
            }
        }
    ]

    # === DICTIONARY (v3.0 Configuration Feature) ===
    dictionary = {
        # Custom dimension configurations (must include status and caption)
        "lineitem_custom_dimensions": {
            "dim_custom1": {
                "status": "enabled",
                "caption": "Audience Segment"
            }
        },
        "campaign_custom_dimensions": {
            "dim_custom1": {
                "status": "enabled",
                "caption": "Campaign Type"
            }
        },
        "meta_custom_dimensions": {
            "dim_custom1": {
                "status": "enabled",
                "caption": "Business Unit"
            }
        },

        # Custom cost configurations (must include status and caption)
        "custom_costs": {
            "cost_custom1": {
                "status": "enabled",
                "caption": "Agency Fees"
            }
        },

        # Custom metric configurations (must include status and caption)
        "custom_metrics": {
            "metric_custom1": {
                "status": "enabled",
                "caption": "Video 50% Views"
            }
        },

        # Standard metrics with formulas
        # Define which standard metrics use formulas and their calculation method
        "standard_metrics": {
            "metric_clicks": {
                "formula_type": "conversion_rate",
                "base_metric": "metric_impressions"
            }
        }
    }

    print(f"\nConfigured v3.0 features:")
    print(f"  - Target audiences: {len(target_audiences)}")
    print(f"  - Target locations: {len(target_locations)}")
    print(f"  - Line items: {len(lineitems)}")
    print(f"  - Dictionary configurations: {len(dictionary)} categories")

    # === CREATE MEDIA PLAN ===
    plan = MediaPlan.create(
        # Required parameters
        campaign_name="Q1 2025 Enterprise Technology Campaign",
        campaign_start_date="2025-01-01",
        campaign_end_date="2025-03-31",
        campaign_budget_total=Decimal("80000.00"),
        created_by_name="examples_user",

        # Campaign details
        campaign_objective="consideration",
        media_plan_name="Advanced v3.0 Feature Showcase",

        # v3.0 ARRAYS
        target_audiences=target_audiences,
        target_locations=target_locations,

        # v3.0 KPIs (Campaign level)
        kpi_name1="CTR",
        kpi_value1=Decimal("2.5"),

        # v3.0 CUSTOM DIMENSIONS (use prefixes for disambiguation)
        meta_dim_custom1="Business Unit: Enterprise Sales",

        campaign_dim_custom1="Campaign Type: Brand Awareness + Lead Gen",

        # v3.0 CUSTOM PROPERTIES (use prefixes)
        meta_custom_properties={
            "approval_status": "approved",
            "budget_source": "marketing_operations",
            "internal_id": "ENT-2025-Q1-001"
        },

        campaign_custom_properties={
            "campaign_manager": "Jane Smith",
            "agency_partner": "Digital Agency Inc",
            "tracking_code": "UTM_Q1_2025_ENT"
        },

        # Line items with all v3.0 features
        lineitems=lineitems,

        # Dictionary configuration
        dictionary=dictionary
    )

    print(f"\n✓ Media plan created successfully with ALL v3.0 features")
    print(f"\nMedia Plan Details:")
    print(f"  - ID: {plan.meta.id}")
    print(f"  - Name: {plan.meta.name}")
    print(f"  - Campaign: {plan.campaign.name}")
    print(f"  - Budget: ${plan.campaign.budget_total:,.2f}")
    print(f"  - Duration: {plan.campaign.start_date} to {plan.campaign.end_date}")

    print(f"\nv3.0 Features Summary:")
    print(f"  - Target Audiences: {len(plan.campaign.target_audiences)}")
    for aud in plan.campaign.target_audiences:
        print(f"    * {aud.name} (Age {aud.demo_age_start}-{aud.demo_age_end}, Pop: {aud.population_size:,})")

    print(f"  - Target Locations: {len(plan.campaign.target_locations)}")
    for loc in plan.campaign.target_locations:
        print(f"    * {loc.name} ({loc.location_type}, {loc.population_percent*100:.0f}% of audience)")

    print(f"  - KPIs Defined:")
    print(f"    * {plan.campaign.kpi_name1}: {plan.campaign.kpi_value1}")

    print(f"  - Custom Dimensions (Meta): {len([d for d in [plan.meta.dim_custom1, plan.meta.dim_custom2, plan.meta.dim_custom3, plan.meta.dim_custom4] if d])}")
    print(f"    * {plan.meta.dim_custom1}")

    print(f"  - Custom Dimensions (Campaign): {len([d for d in [plan.campaign.dim_custom1, plan.campaign.dim_custom2, plan.campaign.dim_custom3] if d])}")
    print(f"    * {plan.campaign.dim_custom1}")

    print(f"  - Line Items: {len(plan.lineitems)}")
    for li in plan.lineitems:
        formulas = len(li.metric_formulas) if li.metric_formulas else 0
        print(f"    * {li.name} (${li.cost_total:,.0f}, {formulas} formulas)")

    print(f"  - Dictionary Categories: {len(plan.dictionary.to_dict()) if plan.dictionary else 0}")

    # Save the media plan
    print(f"\nSaving media plan to workspace...")
    saved_path = plan.save(manager)

    print(f"\n✓ Media plan saved successfully")
    print(f"\nSaved to:")
    print(f"  - Primary file (JSON): {saved_path}")
    print(f"  - Analytics file (Parquet): {saved_path.replace('.json', '.parquet')}")

    # Check if database is enabled in workspace configuration
    db_enabled = manager.config.get('database', {}).get('enabled', False)
    if db_enabled:
        db_table = manager.config['database'].get('table_name', 'media_plans')
        print(f"  - Database: Inserted into table '{db_table}'")
    else:
        print(f"  - Database: Not configured (file-based storage only)")
    print(f"\nNext Steps:")
    print(f"  1. Run examples_load_mediaplan.py to inspect all v3.0 fields")
    print(f"  2. Run examples_edit_mediaplan.py to modify arrays and objects")
    print(f"  3. Run examples_sql_queries.py to analyze by custom dimensions")
    print(f"  4. Run examples_export_mediaplan.py to export with all fields")

    return plan


if __name__ == "__main__":
    print("="*60)
    print("MediaPlanPy v3.0 - Media Plan Creation Examples")
    print("="*60)

    # Load workspace once for all examples
    manager = load_workspace()

    if manager is None:
        print("\nNo workspace loaded. Exiting.")
        exit(0)

    print("\n=== Example 1: Create Minimal Hello World Plan ===")
    plan1 = create_minimal_hello_world_plan(manager)

    print("\n=== Example 2: Create Complex Plan with Loops ===")
    plan2 = create_complex_plan_with_loops(manager)

    print("\n=== Example 3: Create Advanced Plan with ALL v3.0 Features ===")
    plan3 = create_advanced_plan_with_v3_features(manager)

    print("\n" + "="*60)
    print("Media Plan Creation Examples Completed!")
    print("="*60)

    created_plans = [
        f"1. Minimal: {plan1.meta.name} ({plan1.meta.id}) - {len(plan1.lineitems)} line items",
        f"2. Complex: {plan2.meta.name} ({plan2.meta.id}) - {len(plan2.lineitems)} line items",
        f"3. Advanced: {plan3.meta.name} ({plan3.meta.id}) - Full v3.0 features"
    ]

    print(f"\nCreated media plans:")
    for plan_info in created_plans:
        print(f"  {plan_info}")

    print(f"\nTotal plans created: {len(created_plans)}")

    print(f"\nNext Steps:")
    print(f"  - Run examples_load_mediaplan.py to load and inspect these plans")
    print(f"  - Run examples_edit_mediaplan.py to edit plans and manage versions")
    print(f"  - Run examples_export_mediaplan.py to export to JSON/Excel")
    print(f"  - Run examples_list_objects.py to query across all plans")
    print(f"  - Run examples_sql_queries.py for advanced analytics")
