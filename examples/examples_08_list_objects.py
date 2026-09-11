"""
MediaPlanPy Examples - List and Query Objects

This script demonstrates how to query workspace data using MediaPlanPy SDK v3.0.
Shows listing campaigns, media plans, and line items with filters and statistics.

v3.0 Features Demonstrated:
- list_campaigns() with v3.0 columns (KPIs, custom dimensions)
- list_mediaplans() with v3.0 columns and filters
- list_lineitems() flattened view across all plans
- DataFrame output for analysis
- Filter by v3.0 fields (budget, objective, dates, custom dimensions)
- Statistical aggregations

Prerequisites:
- MediaPlanPy SDK v3.0.0+ installed
- pandas library for DataFrame output
- Workspace created (see examples_create_workspace.py)
- Media plans created (see examples_create_mediaplan.py)

How to Run:
1. First run examples_create_workspace.py to create a workspace
2. Then run examples_create_mediaplan.py to create media plans
3. Update WORKSPACE_ID below, or provide when prompted
4. Open this file in your IDE
5. Run the entire script: python examples_list_objects.py

Next Steps After Running:
- Use filters to query specific data
- Export results to CSV for analysis
- Build dashboards and reports
- Run SQL queries for complex analysis
"""

import os
from pathlib import Path

from mediaplanpy.workspace import WorkspaceManager


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


def list_campaigns_json(manager):
    """
    List campaigns as JSON (list of dicts) showing v3.0 fields.

    Use Case:
        When you need campaign data in dictionary format for:
        - API responses
        - JSON export
        - Custom processing
        - Integration with other systems

    v3.0 Features:
        - KPI fields (kpi_name1-5, kpi_value1-5)
        - Custom dimensions (campaign_dim_custom1-5, meta_dim_custom1-5)
        - Summary statistics (total line items, costs, impressions)
        - No deprecated fields (removed audience_*, location_* fields)

    Args:
        manager: Loaded WorkspaceManager instance

    Next Steps:
        - Export to JSON file
        - Send via API
        - Process with custom logic
    """
    print("\n" + "="*60)
    print("Example 1: List Campaigns (JSON/Dict Format)")
    print("="*60)

    print("\nQuerying campaigns...")

    # List campaigns as JSON (list of dicts)
    campaigns = manager.list_campaigns(
        include_stats=True,
        return_dataframe=False  # Return list of dicts
    )

    print(f"\n✓ Found {len(campaigns)} campaigns")

    # Show first few campaigns
    if campaigns:
        print(f"\nFirst campaign:")
        camp = campaigns[0]

        print(f"  - ID: {camp.get('campaign_id', 'N/A')}")
        print(f"  - Name: {camp.get('campaign_name', 'N/A')}")
        print(f"  - Objective: {camp.get('campaign_objective', 'N/A')}")
        print(f"  - Budget: ${camp.get('campaign_budget_total', 0):,.2f}")
        print(f"  - Start date: {camp.get('campaign_start_date', 'N/A')}")
        print(f"  - End date: {camp.get('campaign_end_date', 'N/A')}")

        # Show v3.0 KPI fields
        kpis = []
        for i in range(1, 6):
            kpi_name = camp.get(f'kpi_name{i}')
            kpi_value = camp.get(f'kpi_value{i}')
            if kpi_name:
                kpis.append(f"{kpi_name}={kpi_value}")

        if kpis:
            print(f"  - KPIs: {', '.join(kpis)}")

        # Show v3.0 custom dimensions
        custom_dims = []
        for i in range(1, 6):
            dim_value = camp.get(f'campaign_dim_custom{i}')
            if dim_value:
                custom_dims.append(f"dim_custom{i}={dim_value}")

        if custom_dims:
            print(f"  - Custom dimensions: {', '.join(custom_dims)}")

        # Show statistics if available
        if 'total_line_items' in camp:
            print(f"\nStatistics:")
            print(f"  - Line items: {camp.get('total_line_items', 0)}")
            print(f"  - Total cost: ${camp.get('total_cost', 0):,.2f}")
            if camp.get('total_impressions'):
                print(f"  - Total impressions: {camp.get('total_impressions', 0):,.0f}")

    print(f"\n✓ Successfully listed campaigns in JSON format")

    return campaigns


def list_campaigns_dataframe(manager):
    """
    List campaigns as DataFrame showing v3.0 columns with statistics.

    Use Case:
        When you need campaign data for analysis with pandas:
        - Statistical analysis
        - Data exploration
        - Filtering and grouping
        - Export to CSV/Excel

    v3.0 Features:
        - DataFrame with all v3.0 columns
        - KPI columns (kpi_name1-5, kpi_value1-5)
        - Custom dimension columns
        - Summary statistics
        - Easy filtering and aggregation

    Args:
        manager: Loaded WorkspaceManager instance

    Next Steps:
        - Filter DataFrame: df[df['campaign_budget_total'] > 100000]
        - Group by objective: df.groupby('campaign_objective').sum()
        - Export to CSV: df.to_csv('campaigns.csv')
    """
    print("\n" + "="*60)
    print("Example 2: List Campaigns (DataFrame Format)")
    print("="*60)

    print("\nQuerying campaigns...")

    # List campaigns as DataFrame
    df = manager.list_campaigns(
        include_stats=True,
        return_dataframe=True  # Return pandas DataFrame
    )

    print(f"\n✓ Found {len(df)} campaigns")

    print(f"\nDataFrame Info:")
    print(f"  - Shape: {df.shape[0]} rows × {df.shape[1]} columns")
    print(f"  - Columns: {list(df.columns[:10])} ... (showing first 10)")

    # Show basic statistics
    if len(df) > 0:
        print(f"\nBudget Statistics:")
        print(f"  - Total budget: ${df['campaign_budget_total'].sum():,.2f}")
        print(f"  - Average budget: ${df['campaign_budget_total'].mean():,.2f}")
        print(f"  - Min budget: ${df['campaign_budget_total'].min():,.2f}")
        print(f"  - Max budget: ${df['campaign_budget_total'].max():,.2f}")

        # Show breakdown by objective
        if 'campaign_objective' in df.columns:
            print(f"\nBreakdown by Objective:")
            objective_summary = df.groupby('campaign_objective')['campaign_budget_total'].agg(['count', 'sum'])
            for objective, row in objective_summary.iterrows():
                print(f"  - {objective}: {int(row['count'])} campaigns, ${row['sum']:,.2f}")

    print(f"\n✓ Successfully listed campaigns in DataFrame format")

    return df


def list_mediaplans_with_filters(manager):
    """
    List media plans with advanced filters using v3.0 fields.

    Use Case:
        When you need to query specific media plans based on:
        - Budget range
        - Campaign objective
        - Date range
        - Custom dimensions
        - Version status (current, archived)

    v3.0 Features:
        - Filter by v3.0 fields (KPIs, custom dimensions)
        - Filter by meta fields (is_current, is_archived, parent_id)
        - Combine multiple filters
        - Version-aware queries

    Args:
        manager: Loaded WorkspaceManager instance

    Next Steps:
        - Refine filters for specific use cases
        - Export filtered results
        - Compare plan versions
    """
    print("\n" + "="*60)
    print("Example 3: List Media Plans with Filters")
    print("="*60)

    # ====================
    # FILTER 1: Budget range
    # ====================
    print(f"\n" + "-"*60)
    print("Filter 1: Budget Range")
    print("-"*60)

    print(f"\nQuerying plans with budget > $50,000...")

    # Use the filters parameter with range filter (min/max)
    filtered_plans = manager.list_mediaplans(
        filters={"campaign_budget_total": {"min": 50000}},
        return_dataframe=True
    )

    if len(filtered_plans) > 0:
        print(f"✓ Found {len(filtered_plans)} plans with budget > $50,000")

        print(f"\nTop plan by budget:")
        top_plan = filtered_plans.nlargest(1, 'campaign_budget_total').iloc[0]
        print(f"  - Name: {top_plan['meta_name']}")
        print(f"  - Campaign: {top_plan['campaign_name']}")
        print(f"  - Budget: ${top_plan['campaign_budget_total']:,.2f}")
    else:
        print(f"No media plans found matching filter")

    # ====================
    # FILTER 2: Campaign objective
    # ====================
    print(f"\n" + "-"*60)
    print("Filter 2: Campaign Objective")
    print("-"*60)

    print(f"\nQuerying plans with 'awareness' objective...")

    # Use the filters parameter with exact match on objective
    filtered_plans = manager.list_mediaplans(
        filters={"campaign_objective": "awareness"},
        return_dataframe=True
    )

    print(f"✓ Found {len(filtered_plans)} plans with 'awareness' objective")

    if len(filtered_plans) > 0:
        print(f"\nObjectives found:")
        objectives = filtered_plans['campaign_objective'].unique()
        for obj in objectives:
            count = len(filtered_plans[filtered_plans['campaign_objective'] == obj])
            print(f"  - {obj}: {count} plan(s)")

    # ====================
    # FILTER 3: Date range
    # ====================
    print(f"\n" + "-"*60)
    print("Filter 3: Date Range")
    print("-"*60)

    print(f"\nQuerying plans starting in 2025...")

    # Use the filters parameter with date range filter
    filtered_plans = manager.list_mediaplans(
        filters={"campaign_start_date": {"min": "2025-01-01", "max": "2025-12-31"}},
        return_dataframe=True
    )

    print(f"✓ Found {len(filtered_plans)} plans starting in 2025")

    if len(filtered_plans) > 0:
        print(f"\nDate range:")
        print(f"  - Earliest: {filtered_plans['campaign_start_date'].min()}")
        print(f"  - Latest: {filtered_plans['campaign_start_date'].max()}")

    # ====================
    # FILTER 4: Custom dimensions
    # ====================
    print(f"\n" + "-"*60)
    print("Filter 4: Custom Dimensions")
    print("-"*60)

    print(f"\nQuerying plans with campaign_dim_custom1 matching 'Campaign Type'...")

    # Use the filters parameter with regex filter on custom dimension
    filtered_plans = manager.list_mediaplans(
        filters={"campaign_dim_custom1": {"regex": "^Campaign Type.*"}},
        return_dataframe=True
    )

    print(f"✓ Found {len(filtered_plans)} plans with matching campaign_dim_custom1")

    if len(filtered_plans) > 0:
        print(f"\nCustom dimension values:")
        values = filtered_plans['campaign_dim_custom1'].unique()
        for val in values[:5]:  # Show first 5
            count = len(filtered_plans[filtered_plans['campaign_dim_custom1'] == val])
            print(f"  - {val}: {count} plan(s)")
        if len(values) > 5:
            print(f"  ... and {len(values) - 5} more")

    # ====================
    # FILTER 5: Version status
    # ====================
    print(f"\n" + "-"*60)
    print("Filter 5: Current Versions Only")
    print("-"*60)

    print(f"\nQuerying current (non-archived) plans...")

    # Use the filters parameter with exact match on version fields
    all_plans = manager.list_mediaplans(return_dataframe=True)
    filtered_plans = manager.list_mediaplans(
        filters={"meta_is_current": True, "meta_is_archived": False},
        return_dataframe=True
    )

    print(f"✓ Found {len(filtered_plans)} current, non-archived plans")

    if len(filtered_plans) > 0:
        print(f"\nVersion info:")
        print(f"  - Total plans in workspace: {len(all_plans)}")
        print(f"  - Current plans: {len(filtered_plans)}")
        archived = manager.list_mediaplans(
            filters={"meta_is_archived": True},
            return_dataframe=True
        )
        print(f"  - Archived: {len(archived)}")

    print(f"\n✓ Successfully demonstrated filtering media plans")

    return all_plans


def list_lineitems_with_stats(manager):
    """
    List line items with analysis and grouping.

    Use Case:
        When you need line item details across all plans for:
        - Channel analysis
        - Performance tracking
        - Budget allocation
        - Media mix analysis

    v3.0 Features:
        - All v3.0 line item fields
        - Custom dimensions (dim_custom1-10)
        - Custom costs (cost_custom1-10)
        - Custom metrics (metric_custom1-10)
        - Extended metrics (engagements, reach, views, etc.)
        - Flattened view across all campaigns

    Args:
        manager: Loaded WorkspaceManager instance

    Next Steps:
        - Group by channel for mix analysis
        - Calculate CPM, CPC, CTR
        - Export for detailed analysis
        - Build performance dashboards
    """
    print("\n" + "="*60)
    print("Example 4: List Line Items with Analysis")
    print("="*60)

    print("\nQuerying line items across all plans...")

    # List all line items
    df = manager.list_lineitems(return_dataframe=True)

    print(f"\n✓ Found {len(df)} line items across all plans")

    if len(df) > 0:
        print(f"\nDataFrame Info:")
        print(f"  - Shape: {df.shape[0]} rows × {df.shape[1]} columns")

        # ====================
        # ANALYSIS 1: Basic statistics
        # ====================
        print(f"\n" + "-"*60)
        print("Basic Statistics")
        print("-"*60)

        print(f"\nCost Summary:")
        print(f"  - Total cost: ${df['lineitem_cost_total'].sum():,.2f}")
        print(f"  - Average cost: ${df['lineitem_cost_total'].mean():,.2f}")
        print(f"  - Min cost: ${df['lineitem_cost_total'].min():,.2f}")
        print(f"  - Max cost: ${df['lineitem_cost_total'].max():,.2f}")

        if 'lineitem_metric_impressions' in df.columns and df['lineitem_metric_impressions'].notna().any():
            print(f"\nImpressions Summary:")
            total_imp = df['lineitem_metric_impressions'].sum()
            print(f"  - Total impressions: {total_imp:,.0f}")
            print(f"  - Average impressions: {df['lineitem_metric_impressions'].mean():,.0f}")

        # ====================
        # ANALYSIS 2: Channel breakdown
        # ====================
        print(f"\n" + "-"*60)
        print("Channel Breakdown")
        print("-"*60)

        if 'lineitem_channel' in df.columns:
            channel_summary = df.groupby('lineitem_channel').agg({
                'lineitem_cost_total': ['count', 'sum'],
                'lineitem_metric_impressions': 'sum'
            }).round(2)

            print(f"\nBy Channel:")
            for channel in channel_summary.index:
                line_count = channel_summary.loc[channel, ('lineitem_cost_total', 'count')]
                total_cost = channel_summary.loc[channel, ('lineitem_cost_total', 'sum')]
                print(f"  - {channel}:")
                print(f"    • Line items: {int(line_count)}")
                print(f"    • Total cost: ${total_cost:,.2f}")

                if ('lineitem_metric_impressions', 'sum') in channel_summary.columns:
                    total_imp = channel_summary.loc[channel, ('lineitem_metric_impressions', 'sum')]
                    if total_imp > 0:
                        cpm = (total_cost / total_imp) * 1000
                        print(f"    • Total impressions: {total_imp:,.0f}")
                        print(f"    • CPM: ${cpm:.2f}")

        # ====================
        # ANALYSIS 3: Custom dimensions
        # ====================
        print(f"\n" + "-"*60)
        print("Custom Dimensions Analysis")
        print("-"*60)

        custom_dims_found = []
        for i in range(1, 11):
            col_name = f'lineitem_dim_custom{i}'
            if col_name in df.columns and df[col_name].notna().any():
                custom_dims_found.append(col_name)

        if custom_dims_found:
            print(f"\nFound {len(custom_dims_found)} custom dimensions with data:")
            for dim in custom_dims_found[:3]:  # Show first 3
                unique_values = df[dim].dropna().unique()
                print(f"  - {dim}: {len(unique_values)} unique value(s)")
                if len(unique_values) <= 3:
                    for val in unique_values:
                        count = len(df[df[dim] == val])
                        print(f"    • {val}: {count} line item(s)")
        else:
            print(f"\nNo custom dimensions with data found")

    print(f"\n✓ Successfully analyzed line items")

    return df


if __name__ == "__main__":
    print("="*60)
    print("MediaPlanPy v3.0 - List and Query Objects Examples")
    print("="*60)

    # Load workspace ONCE
    print("\nLoading workspace...")
    manager = load_workspace()

    if manager is None:
        print("\nNo workspace loaded. Exiting.")
        print("\nTo run these examples:")
        print("  1. Run examples_create_workspace.py first")
        print("  2. Run examples_create_mediaplan.py to create plans")
        print("  3. Update WORKSPACE_ID at top of this file")
        print("  4. Or provide value when prompted")
        exit(0)

    # Run examples
    campaigns_json = list_campaigns_json(manager)

    campaigns_df = list_campaigns_dataframe(manager)

    plans_df = list_mediaplans_with_filters(manager)

    lineitems_df = list_lineitems_with_stats(manager)

    print("\n" + "="*60)
    print("List and Query Objects Examples Completed!")
    print("="*60)

    print(f"\nWhat We Demonstrated:")
    print(f"  1. Listed campaigns in JSON format")
    print(f"  2. Listed campaigns in DataFrame format with statistics")
    print(f"  3. Filtered media plans by budget, objective, dates, custom dimensions")
    print(f"  4. Analyzed line items by channel with statistics")
    print(f"  5. Used v3.0 fields (KPIs, custom dimensions)")
    print(f"  6. Performed DataFrame analysis and grouping")

    print(f"\nNext Steps:")
    print(f"  - Export to CSV: df.to_csv('campaigns.csv')")
    print(f"  - Run SQL queries: manager.sql_query('SELECT ...')")
    print(f"  - Build dashboards from query results")
    print(f"  - Create custom filters for your use cases")
