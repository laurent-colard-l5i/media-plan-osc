"""
MediaPlanPy Examples - Load Media Plan

This script demonstrates how to load and inspect media plans using MediaPlanPy SDK v3.0.
Loading media plans allows you to read all properties, including v3.0 arrays and nested objects.

v3.0 Features Demonstrated:
- MediaPlan.load() method with workspace integration
- Loading by media_plan_id or campaign_id
- Comprehensive property inspection (meta, campaign, line items)
- Access to v3.0 arrays (target_audiences, target_locations)
- Access to v3.0 nested objects (metric_formulas, dictionary)
- Inspection of all v3.0 field categories (KPIs, custom dimensions, custom properties)

Prerequisites:
- MediaPlanPy SDK v3.0.2+ installed
- Workspace created (see examples_create_workspace.py)
- Media plan created (see examples_create_mediaplan.py)

How to Run:
1. First run examples_create_workspace.py to create a workspace
2. Then run examples_create_mediaplan.py to create media plans
3. Update WORKSPACE_ID and MEDIAPLAN_ID constants below (or enter when prompted)
4. Open this file in your IDE
5. Run the entire script: python examples_load_mediaplan.py
6. Or run individual functions by calling them from __main__

Next Steps After Running:
- Understand all available v3.0 properties
- Use this as reference for accessing specific fields
- Proceed to examples_edit_mediaplan.py to modify properties
"""

import os
from pathlib import Path
from datetime import datetime
from decimal import Decimal

from mediaplanpy.workspace import WorkspaceManager
from mediaplanpy.models import MediaPlan


# ============================================================================
# USER CONFIGURATION
# Update these values after running examples_create_workspace.py and examples_create_mediaplan.py
# ============================================================================

# Workspace ID - Copy from examples_create_workspace.py output
WORKSPACE_ID = "workspace_b92ee88b"

# Media Plan ID - Copy from examples_create_mediaplan.py output
MEDIAPLAN_ID = "mediaplan_865f445e"

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
    print(f"  1. Enter the value now (paste from previous examples output)")
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


def load_workspace_and_plan():
    """
    Load workspace and media plan once for use across all examples.

    Returns:
        Tuple of (WorkspaceManager, MediaPlan) or (None, None) if user skips
    """
    # Get workspace ID (prompt once)
    workspace_id = get_configuration_value(
        'WORKSPACE_ID',
        'Enter workspace ID',
        'workspace_abc12345'
    )

    if workspace_id is None:
        return None, None

    # Get media plan ID (prompt once)
    mediaplan_id = get_configuration_value(
        'MEDIAPLAN_ID',
        'Enter media plan ID',
        'mp_abc12345'
    )

    if mediaplan_id is None:
        return None, None

    print(f"\nLoading workspace: {workspace_id}")
    manager = WorkspaceManager()
    manager.load(workspace_id=workspace_id)
    print(f"✓ Workspace loaded successfully")

    print(f"\nLoading media plan: {mediaplan_id}")
    plan = MediaPlan.load(manager, media_plan_id=mediaplan_id)
    print(f"✓ Media plan loaded successfully")

    return manager, plan


def load_by_mediaplan_id(manager, plan):
    """
    Display basic information about a loaded media plan.

    Use Case:
        Quick overview of a media plan's key properties and v3.0 features.

    v3.0 Features:
        - MediaPlan.load() method with workspace integration
        - Schema version validation (v3.0)
        - Automatic deserialization of arrays and nested objects
        - Full object model reconstruction from storage

    Args:
        manager: Loaded WorkspaceManager instance
        plan: Loaded MediaPlan object

    Next Steps:
        - Access any property: plan.meta.name, plan.campaign.name, etc.
        - Iterate over line items: for li in plan.lineitems
        - Iterate over arrays: for aud in plan.campaign.target_audiences
        - Access nested objects: plan.lineitems[0].metric_formulas
    """
    print("\n" + "="*60)
    print("Media Plan Overview")
    print("="*60)

    print(f"\nBasic Information:")
    print(f"  - Media plan ID: {plan.meta.id}")
    print(f"  - Media plan name: {plan.meta.name}")
    print(f"  - Schema version: {plan.meta.schema_version}")
    print(f"  - Campaign: {plan.campaign.name}")
    print(f"  - Line items: {len(plan.lineitems)}")

    # Show v3.0 features present
    print(f"\nv3.0 Features Present:")
    has_audiences = plan.campaign.target_audiences and len(plan.campaign.target_audiences) > 0
    print(f"  - Target audiences: {len(plan.campaign.target_audiences) if has_audiences else 0}")

    has_locations = plan.campaign.target_locations and len(plan.campaign.target_locations) > 0
    print(f"  - Target locations: {len(plan.campaign.target_locations) if has_locations else 0}")

    has_kpis = any([plan.campaign.kpi_name1, plan.campaign.kpi_name2, plan.campaign.kpi_name3,
                    plan.campaign.kpi_name4, plan.campaign.kpi_name5])
    print(f"  - KPIs defined: {has_kpis}")

    has_custom_dims = any([plan.campaign.dim_custom1, plan.campaign.dim_custom2, plan.campaign.dim_custom3,
                           plan.campaign.dim_custom4, plan.campaign.dim_custom5])
    print(f"  - Custom dimensions: {has_custom_dims}")

    has_formulas = any(li.metric_formulas for li in plan.lineitems if li.metric_formulas)
    print(f"  - Metric formulas: {has_formulas}")

    has_dictionary = plan.dictionary is not None
    print(f"  - Dictionary configured: {has_dictionary}")

    print(f"\nNext Steps:")
    print(f"  - Run load_and_inspect_all_properties() to see all fields")
    print(f"  - Access properties: plan.meta.name, plan.campaign.budget_total")
    print(f"  - Iterate arrays: for aud in plan.campaign.target_audiences")
    print(f"  - Edit and save: plan.campaign.name = 'New Name'; plan.save(manager)")

    return plan


def load_and_inspect_all_properties(manager, plan):
    """
    Inspect ALL v3.0 properties of a loaded media plan comprehensively.

    Use Case:
        Understanding the complete v3.0 data model and available fields.
        Reference for accessing specific properties in your own code.

    v3.0 Features:
        - Complete meta properties inspection
        - Complete campaign properties inspection (basic + v3.0)
        - Target audiences array inspection (all 13+ attributes)
        - Target locations array inspection (all attributes)
        - Line items inspection (all properties including v3.0)
        - Metric formulas inspection (nested objects)
        - Dictionary configuration inspection

    Args:
        manager: Loaded WorkspaceManager instance
        plan: Loaded MediaPlan object

    Next Steps:
        - Use this as reference for your own property access
        - Edit specific properties (see examples_edit_mediaplan.py)
        - Export with all fields (see examples_export_mediaplan.py)
    """
    print("\n" + "="*60)
    print("Comprehensive Property Inspection")
    print("="*60)

    print(f"\nInspecting: {plan.meta.name}")

    # ====================
    # META PROPERTIES
    # ====================
    print(f"\n" + "="*60)
    print("META PROPERTIES")
    print("="*60)

    print(f"\nCore Meta Fields:")
    print(f"  - id: {plan.meta.id}")
    print(f"  - schema_version: {plan.meta.schema_version}")
    print(f"  - name: {plan.meta.name}")
    print(f"  - comments: {plan.meta.comments or '(not set)'}")

    print(f"\nCreation Tracking:")
    print(f"  - created_by_name: {plan.meta.created_by_name}")
    print(f"  - created_by_id: {plan.meta.created_by_id or '(not set)'}")
    print(f"  - created_at: {plan.meta.created_at}")

    print(f"\nVersion Management:")
    print(f"  - is_current: {plan.meta.is_current if hasattr(plan.meta, 'is_current') else 'N/A'}")
    print(f"  - is_archived: {plan.meta.is_archived if hasattr(plan.meta, 'is_archived') else 'N/A'}")
    print(f"  - parent_id: {plan.meta.parent_id if hasattr(plan.meta, 'parent_id') and plan.meta.parent_id else '(no parent)'}")

    print(f"\nMeta Custom Dimensions:")
    print(f"  - dim_custom1: {plan.meta.dim_custom1 or '(not set)'}")
    print(f"  - dim_custom2: {plan.meta.dim_custom2 or '(not set)'}")
    print(f"  - dim_custom3: {plan.meta.dim_custom3 or '(not set)'}")
    print(f"  - dim_custom4: {plan.meta.dim_custom4 or '(not set)'}")
    print(f"  - dim_custom5: {plan.meta.dim_custom5 or '(not set)'}")

    print(f"\nMeta Custom Properties:")
    if plan.meta.custom_properties:
        for key, value in plan.meta.custom_properties.items():
            print(f"  - {key}: {value}")
    else:
        print(f"  (none set)")

    # ====================
    # CAMPAIGN PROPERTIES
    # ====================
    print(f"\n" + "="*60)
    print("CAMPAIGN PROPERTIES")
    print("="*60)

    print(f"\nCore Campaign Fields:")
    print(f"  - id: {plan.campaign.id}")
    print(f"  - name: {plan.campaign.name}")
    print(f"  - objective: {plan.campaign.objective or '(not set)'}")
    print(f"  - start_date: {plan.campaign.start_date}")
    print(f"  - end_date: {plan.campaign.end_date}")
    print(f"  - budget_total: ${plan.campaign.budget_total:,.2f}")
    print(f"  - budget_currency: {plan.campaign.budget_currency or '(not set)'}")

    print(f"\nProduct Information:")
    print(f"  - product_id: {plan.campaign.product_id or '(not set)'}")
    print(f"  - product_name: {plan.campaign.product_name or '(not set)'}")
    print(f"  - product_description: {plan.campaign.product_description or '(not set)'}")

    print(f"\nAgency Information:")
    print(f"  - agency_id: {plan.campaign.agency_id or '(not set)'}")
    print(f"  - agency_name: {plan.campaign.agency_name or '(not set)'}")

    print(f"\nAdvertiser Information:")
    print(f"  - advertiser_id: {plan.campaign.advertiser_id or '(not set)'}")
    print(f"  - advertiser_name: {plan.campaign.advertiser_name or '(not set)'}")

    print(f"\nCampaign Type:")
    print(f"  - campaign_type_id: {plan.campaign.campaign_type_id or '(not set)'}")
    print(f"  - campaign_type_name: {plan.campaign.campaign_type_name or '(not set)'}")

    print(f"\nWorkflow Status:")
    print(f"  - workflow_status_id: {plan.campaign.workflow_status_id or '(not set)'}")
    print(f"  - workflow_status_name: {plan.campaign.workflow_status_name or '(not set)'}")

    # v3.0 KPIs
    print(f"\nv3.0 KPIs:")
    kpis_defined = []
    if plan.campaign.kpi_name1:
        kpis_defined.append(f"{plan.campaign.kpi_name1}: {plan.campaign.kpi_value1}")
    if plan.campaign.kpi_name2:
        kpis_defined.append(f"{plan.campaign.kpi_name2}: {plan.campaign.kpi_value2}")
    if plan.campaign.kpi_name3:
        kpis_defined.append(f"{plan.campaign.kpi_name3}: {plan.campaign.kpi_value3}")
    if plan.campaign.kpi_name4:
        kpis_defined.append(f"{plan.campaign.kpi_name4}: {plan.campaign.kpi_value4}")
    if plan.campaign.kpi_name5:
        kpis_defined.append(f"{plan.campaign.kpi_name5}: {plan.campaign.kpi_value5}")

    if kpis_defined:
        for kpi in kpis_defined:
            print(f"  - {kpi}")
    else:
        print(f"  (no KPIs defined)")

    # Campaign custom dimensions
    print(f"\nCampaign Custom Dimensions:")
    print(f"  - dim_custom1: {plan.campaign.dim_custom1 or '(not set)'}")
    print(f"  - dim_custom2: {plan.campaign.dim_custom2 or '(not set)'}")
    print(f"  - dim_custom3: {plan.campaign.dim_custom3 or '(not set)'}")
    print(f"  - dim_custom4: {plan.campaign.dim_custom4 or '(not set)'}")
    print(f"  - dim_custom5: {plan.campaign.dim_custom5 or '(not set)'}")

    # Campaign custom properties
    print(f"\nCampaign Custom Properties:")
    if plan.campaign.custom_properties:
        for key, value in plan.campaign.custom_properties.items():
            print(f"  - {key}: {value}")
    else:
        print(f"  (none set)")

    # ====================
    # TARGET AUDIENCES (v3.0)
    # ====================
    print(f"\n" + "="*60)
    print("TARGET AUDIENCES (v3.0)")
    print("="*60)

    if plan.campaign.target_audiences and len(plan.campaign.target_audiences) > 0:
        for idx, aud in enumerate(plan.campaign.target_audiences, 1):
            print(f"\nAudience {idx}: {aud.name}")
            print(f"  - description: {aud.description or '(not set)'}")

            # Demographics
            if aud.demo_age_start or aud.demo_age_end:
                print(f"  - demo_age_range: {aud.demo_age_start or 'N/A'} - {aud.demo_age_end or 'N/A'}")
            if aud.demo_gender:
                print(f"  - demo_gender: {aud.demo_gender}")
            if aud.demo_attributes:
                print(f"  - demo_attributes: {aud.demo_attributes}")

            # Interests, Intent, Purchase
            if aud.interest_attributes:
                print(f"  - interest_attributes: {aud.interest_attributes}")
            if aud.intent_attributes:
                print(f"  - intent_attributes: {aud.intent_attributes}")
            if aud.purchase_attributes:
                print(f"  - purchase_attributes: {aud.purchase_attributes}")

            # Content
            if aud.content_attributes:
                print(f"  - content_attributes: {aud.content_attributes}")

            # Exclusions and Extensions
            if aud.exclusion_list:
                print(f"  - exclusion_list: {aud.exclusion_list}")
            if aud.extension_approach:
                print(f"  - extension_approach: {aud.extension_approach}")

            # Population
            if aud.population_size:
                print(f"  - population_size: {aud.population_size:,.0f}")
    else:
        print(f"\n(no target audiences defined)")

    # ====================
    # TARGET LOCATIONS (v3.0)
    # ====================
    print(f"\n" + "="*60)
    print("TARGET LOCATIONS (v3.0)")
    print("="*60)

    if plan.campaign.target_locations and len(plan.campaign.target_locations) > 0:
        for idx, loc in enumerate(plan.campaign.target_locations, 1):
            print(f"\nLocation {idx}: {loc.name}")
            print(f"  - description: {loc.description or '(not set)'}")
            print(f"  - location_type: {loc.location_type or '(not set)'}")

            if loc.location_list:
                print(f"  - location_list: {', '.join(loc.location_list)}")

            if loc.exclusion_type:
                print(f"  - exclusion_type: {loc.exclusion_type}")
            if loc.exclusion_list:
                print(f"  - exclusion_list: {', '.join(loc.exclusion_list)}")

            if loc.population_percent:
                print(f"  - population_percent: {loc.population_percent * 100:.1f}%")
    else:
        print(f"\n(no target locations defined)")

    # ====================
    # LINE ITEMS
    # ====================
    print(f"\n" + "="*60)
    print(f"LINE ITEMS ({len(plan.lineitems)} items)")
    print("="*60)

    for idx, li in enumerate(plan.lineitems, 1):
        print(f"\nLine Item {idx}: {li.name}")

        # Core fields
        print(f"  - id: {li.id}")
        print(f"  - start_date: {li.start_date}")
        print(f"  - end_date: {li.end_date}")

        # Channel and media type
        print(f"  - channel: {li.channel or '(not set)'}")
        print(f"  - vehicle: {li.vehicle or '(not set)'}")
        print(f"  - partner: {li.partner or '(not set)'}")

        # Ad format and inventory
        if li.adformat:
            print(f"  - adformat: {li.adformat}")
        if li.inventory:
            print(f"  - inventory: {li.inventory}")

        # Buy information (v3.0)
        if li.buy_type:
            print(f"  - buy_type: {li.buy_type}")
        if li.buy_commitment:
            print(f"  - buy_commitment: {li.buy_commitment}")

        # Costs
        print(f"  - cost_total: ${li.cost_total:,.2f}")
        if li.cost_minimum:
            print(f"  - cost_minimum: ${li.cost_minimum:,.2f}")
        if li.cost_maximum:
            print(f"  - cost_maximum: ${li.cost_maximum:,.2f}")
        if li.cost_currency_exchange_rate:
            print(f"  - cost_currency_exchange_rate: {li.cost_currency_exchange_rate}")

        # Custom costs (show only if set)
        custom_costs = []
        for i in range(1, 11):
            cost_name = getattr(li, f"cost_name{i}", None)
            cost_value = getattr(li, f"cost_custom{i}", None)
            if cost_name and cost_value:
                custom_costs.append(f"{cost_name}: ${cost_value:,.2f}")
        if custom_costs:
            print(f"  - custom_costs: {', '.join(custom_costs)}")

        # Metrics
        if li.metric_impressions:
            print(f"  - metric_impressions: {li.metric_impressions:,.0f}")
        if li.metric_clicks:
            print(f"  - metric_clicks: {li.metric_clicks:,.0f}")

        # Enhanced metrics (v3.0)
        if li.metric_reach:
            print(f"  - metric_reach: {li.metric_reach:,.0f}")
        if li.metric_view_starts:
            print(f"  - metric_view_starts: {li.metric_view_starts:,.0f}")
        if li.metric_view_completions:
            print(f"  - metric_view_completions: {li.metric_view_completions:,.0f}")

        # Custom metrics (show only if set)
        custom_metrics = []
        for i in range(1, 11):
            metric_name = getattr(li, f"metric_name{i}", None)
            metric_value = getattr(li, f"metric_custom{i}", None)
            if metric_name and metric_value:
                custom_metrics.append(f"{metric_name}: {metric_value:,.0f}")
        if custom_metrics:
            print(f"  - custom_metrics: {', '.join(custom_metrics)}")

        # Metric Formulas (v3.0)
        if li.metric_formulas and len(li.metric_formulas) > 0:
            print(f"  - metric_formulas ({len(li.metric_formulas)}):")
            for formula_name, formula_obj in li.metric_formulas.items():
                print(f"    * {formula_name}: {formula_obj.formula_type}")
                if formula_obj.base_metric:
                    print(f"      - base_metric: {formula_obj.base_metric}")
                if formula_obj.coefficient:
                    print(f"      - coefficient: {formula_obj.coefficient}")

        # Line item custom dimensions
        custom_dims = []
        for i in range(1, 6):
            dim = getattr(li, f"dim_custom{i}", None)
            if dim:
                custom_dims.append(f"dim_custom{i}: {dim}")
        if custom_dims:
            print(f"  - custom_dimensions: {', '.join(custom_dims)}")

        # Line item custom properties
        if li.custom_properties:
            print(f"  - custom_properties:")
            for key, value in li.custom_properties.items():
                print(f"    * {key}: {value}")

    # ====================
    # DICTIONARY (v3.0)
    # ====================
    print(f"\n" + "="*60)
    print("DICTIONARY CONFIGURATION (v3.0)")
    print("="*60)

    if plan.dictionary:
        dict_data = plan.dictionary.to_dict()

        # Custom dimensions configurations
        if dict_data.get('lineitem_custom_dimensions'):
            print(f"\nLine Item Custom Dimensions:")
            for dim, config in dict_data['lineitem_custom_dimensions'].items():
                if isinstance(config, dict):
                    status = config.get('status', 'unknown')
                    caption = config.get('caption', '(no caption)')
                    print(f"  - {dim}: {caption} (status: {status})")
                else:
                    print(f"  - {dim}: {config}")

        if dict_data.get('campaign_custom_dimensions'):
            print(f"\nCampaign Custom Dimensions:")
            for dim, config in dict_data['campaign_custom_dimensions'].items():
                if isinstance(config, dict):
                    status = config.get('status', 'unknown')
                    caption = config.get('caption', '(no caption)')
                    print(f"  - {dim}: {caption} (status: {status})")
                else:
                    print(f"  - {dim}: {config}")

        if dict_data.get('meta_custom_dimensions'):
            print(f"\nMeta Custom Dimensions:")
            for dim, config in dict_data['meta_custom_dimensions'].items():
                if isinstance(config, dict):
                    status = config.get('status', 'unknown')
                    caption = config.get('caption', '(no caption)')
                    print(f"  - {dim}: {caption} (status: {status})")
                else:
                    print(f"  - {dim}: {config}")

        # Custom costs configurations
        if dict_data.get('custom_costs'):
            print(f"\nCustom Costs:")
            for cost, config in dict_data['custom_costs'].items():
                if isinstance(config, dict):
                    status = config.get('status', 'unknown')
                    caption = config.get('caption', '(no caption)')
                    print(f"  - {cost}: {caption} (status: {status})")
                else:
                    print(f"  - {cost}: {config}")

        # Custom metrics configurations
        if dict_data.get('custom_metrics'):
            print(f"\nCustom Metrics:")
            for metric, config in dict_data['custom_metrics'].items():
                if isinstance(config, dict):
                    status = config.get('status', 'unknown')
                    caption = config.get('caption', '(no caption)')
                    # Also show formula info if present
                    if config.get('formula_type'):
                        formula_type = config.get('formula_type')
                        base_metric = config.get('base_metric', 'N/A')
                        print(f"  - {metric}: {caption} (status: {status}, formula: {formula_type}, base: {base_metric})")
                    else:
                        print(f"  - {metric}: {caption} (status: {status})")
                else:
                    print(f"  - {metric}: {config}")

        # Standard metrics with formulas (if configured at dictionary level)
        if dict_data.get('standard_metrics'):
            print(f"\nStandard Metrics (with formulas):")
            for metric, config in dict_data['standard_metrics'].items():
                if isinstance(config, dict):
                    formula_type = config.get('formula_type', 'N/A')
                    base_metric = config.get('base_metric', 'N/A')
                    print(f"  - {metric}: formula={formula_type}, base={base_metric}")
                else:
                    print(f"  - {metric}: {config}")

        # Other calculated metrics (legacy or custom formula definitions)
        known_keys = {'lineitem_custom_dimensions', 'campaign_custom_dimensions', 'meta_custom_dimensions',
                      'custom_costs', 'custom_metrics', 'standard_metrics'}
        other_keys = [k for k in dict_data.keys() if k not in known_keys]
        if other_keys:
            print(f"\nCalculated Metrics:")
            for key in other_keys:
                print(f"  - {key}: {dict_data[key]}")
    else:
        print(f"\n(no dictionary configured)")

    # ====================
    # SUMMARY
    # ====================
    print(f"\n" + "="*60)
    print("INSPECTION COMPLETE")
    print("="*60)

    print(f"\nv3.0 Feature Summary:")
    print(f"  - Target audiences: {len(plan.campaign.target_audiences) if plan.campaign.target_audiences else 0}")
    print(f"  - Target locations: {len(plan.campaign.target_locations) if plan.campaign.target_locations else 0}")

    kpi_count = sum([1 for i in range(1, 6) if getattr(plan.campaign, f'kpi_name{i}')])
    print(f"  - KPIs defined: {kpi_count}")

    formula_count = sum([len(li.metric_formulas) for li in plan.lineitems if li.metric_formulas])
    print(f"  - Metric formulas: {formula_count}")

    print(f"  - Dictionary: {'Yes' if plan.dictionary else 'No'}")

    print(f"\nNext Steps:")
    print(f"  - Edit properties: see examples_edit_mediaplan.py")
    print(f"  - Export with all fields: see examples_export_mediaplan.py")
    print(f"  - Query by custom dimensions: see examples_sql_queries.py")

    return plan


def load_by_campaign_id(manager, campaign_id):
    """
    Load a media plan by campaign ID instead of media plan ID.

    Use Case:
        When you know the campaign ID but not the specific media plan ID.
        The SDK resolves the campaign to its current media plan automatically
        by querying workspace.list_campaigns() and finding the plan where
        is_current=True for that campaign.

    v3.0 Features:
        - MediaPlan.load(campaign_id=...) with automatic resolution
        - Workspace query integration to find current plan for a campaign
        - Seamless loading identical to media_plan_id approach

    Args:
        manager: Loaded WorkspaceManager instance
        campaign_id: The campaign ID to look up (e.g., from the previously loaded plan)

    Next Steps:
        - Use the loaded plan exactly as if loaded by media_plan_id
        - Access all properties: plan.meta.id, plan.campaign.name, etc.
        - This is useful in workflows where campaign IDs are the primary identifier
    """
    print("\n" + "="*60)
    print("Load Media Plan by Campaign ID")
    print("="*60)

    print(f"\nLoading media plan for campaign: {campaign_id}")
    print(f"  (The SDK will query the workspace to find the current media plan")
    print(f"   for this campaign and load it automatically.)")

    # Load the media plan using campaign_id
    plan = MediaPlan.load(manager, campaign_id=campaign_id)

    print(f"\nResolved to media plan:")
    print(f"  - Media plan ID: {plan.meta.id}")
    print(f"  - Media plan name: {plan.meta.name}")
    print(f"  - Campaign ID: {plan.campaign.id}")
    print(f"  - Campaign name: {plan.campaign.name}")
    print(f"  - Is current: {plan.meta.is_current}")
    print(f"  - Line items: {len(plan.lineitems)}")

    print(f"\nHow it works:")
    print(f"  1. SDK calls workspace.list_campaigns(filters={{'campaign_id': '{campaign_id}'}})")
    print(f"  2. Finds the current media plan's meta_id for that campaign")
    print(f"  3. Loads the media plan file using the resolved meta_id")

    print(f"\nThis is equivalent to calling:")
    print(f"  MediaPlan.load(manager, media_plan_id='{plan.meta.id}')")

    return plan


if __name__ == "__main__":
    print("="*60)
    print("MediaPlanPy v3.0 - Load Media Plan Examples")
    print("="*60)

    # Load workspace and media plan once for all examples
    manager, plan = load_workspace_and_plan()

    if manager is None or plan is None:
        print("\nNo workspace or media plan loaded. Exiting.")
        exit(0)

    print("\n=== Example 1: Media Plan Overview ===")
    load_by_mediaplan_id(manager, plan)

    print("\n=== Example 2: Comprehensive Property Inspection ===")
    load_and_inspect_all_properties(manager, plan)

    print("\n=== Example 3: Load by Campaign ID ===")
    load_by_campaign_id(manager, plan.campaign.id)

    print("\n" + "="*60)
    print("Load Examples Completed!")
    print("="*60)
    print(f"\nYou've learned how to:")
    print(f"  - Load media plans by media plan ID")
    print(f"  - Load media plans by campaign ID")
    print(f"  - Access all v3.0 properties")
    print(f"  - Inspect arrays (target_audiences, target_locations)")
    print(f"  - Inspect nested objects (metric_formulas, dictionary)")
    print(f"\nNext Steps:")
    print(f"  - Run examples_edit_mediaplan.py to modify properties")
    print(f"  - Run examples_export_mediaplan.py to export with all fields")
