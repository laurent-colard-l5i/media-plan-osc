"""
MediaPlanPy Examples - SQL Queries

This script demonstrates how to run SQL queries against workspace data using MediaPlanPy SDK v3.0.
Shows simple and complex SQL queries with DuckDB for analytics and reporting.

v3.0 Features Demonstrated:
- sql_query() method with Parquet files
- Query v3.0 columns (KPIs, custom dimensions, custom metrics/costs)
- Multi-dimensional aggregations
- Custom dimension grouping
- KPI analysis
- Pattern matching with {*} placeholder
- Channel mix analysis
- Time-based analysis

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
5. Run the entire script: python examples_sql_queries.py

Next Steps After Running:
- Create custom SQL queries for your analysis needs
- Export results to CSV/Excel
- Build dashboards and reports
- Combine with Python data processing
"""

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


def simple_sql_queries(manager):
    """
    Demonstrate simple SQL queries for common use cases.

    Use Case:
        When you need straightforward data retrieval:
        - SELECT all campaigns with v3.0 fields
        - Aggregate budget by objective
        - Filter by custom dimensions
        - Simple statistics

    v3.0 Features:
        - Query v3.0 columns (KPIs, custom dimensions)
        - {*} placeholder for all Parquet files
        - DataFrame output for analysis

    Args:
        manager: Loaded WorkspaceManager instance

    Next Steps:
        - Modify queries for specific fields
        - Add WHERE clauses for filtering
        - Export results to CSV
    """
    print("\n" + "="*60)
    print("Example 1: Simple SQL Queries")
    print("="*60)

    # ====================
    # QUERY 1: SELECT all campaigns
    # ====================
    print(f"\n" + "-"*60)
    print("Query 1: SELECT All Campaigns with v3.0 Fields")
    print("-"*60)

    query = """
    SELECT DISTINCT
        campaign_id,
        campaign_name,
        campaign_objective,
        campaign_budget_total,
        campaign_start_date,
        campaign_end_date,
        campaign_kpi_name1,
        campaign_kpi_value1,
        campaign_dim_custom1
    FROM {*}
    WHERE meta_is_archived = FALSE
    ORDER BY campaign_name
    """

    print(f"\nSQL Query:")
    print(query)

    df = manager.sql_query(query, return_dataframe=True)

    print(f"\n✓ Query returned {len(df)} campaigns")

    if len(df) > 0:
        print(f"\nFirst campaign:")
        camp = df.iloc[0]
        print(f"  - ID: {camp['campaign_id']}")
        print(f"  - Name: {camp['campaign_name']}")
        print(f"  - Budget: ${camp['campaign_budget_total']:,.2f}")
        if camp['campaign_kpi_name1']:
            print(f"  - KPI 1: {camp['campaign_kpi_name1']} = {camp['campaign_kpi_value1']}")

    # ====================
    # QUERY 2: Aggregate cost by objective
    # ====================
    print(f"\n" + "-"*60)
    print("Query 2: Aggregate Cost by Objective")
    print("-"*60)

    query = """
    SELECT
        campaign_objective,
        COUNT(DISTINCT campaign_id) as campaign_count,
        COUNT(DISTINCT lineitem_id) as lineitem_count,
        SUM(lineitem_cost_total) as total_cost,
        AVG(lineitem_cost_total) as avg_cost_per_lineitem
    FROM {*}
    WHERE meta_is_archived = FALSE
      AND (is_placeholder = FALSE OR is_placeholder IS NULL)
    GROUP BY campaign_objective
    ORDER BY total_cost DESC
    """

    print(f"\nSQL Query:")
    print(query)

    df = manager.sql_query(query, return_dataframe=True)

    print(f"\n✓ Query returned {len(df)} objectives")

    if len(df) > 0:
        print(f"\nResults:")
        for _, row in df.iterrows():
            print(f"  - {row['campaign_objective']}:")
            print(f"    • Campaigns: {int(row['campaign_count'])}")
            print(f"    • Line items: {int(row['lineitem_count'])}")
            print(f"    • Total cost: ${row['total_cost']:,.2f}")
            print(f"    • Avg cost per line item: ${row['avg_cost_per_lineitem']:,.2f}")

    # ====================
    # QUERY 3: Filter by custom dimension
    # ====================
    print(f"\n" + "-"*60)
    print("Query 3: Filter by Custom Dimension")
    print("-"*60)

    query = """
    SELECT DISTINCT
        campaign_name,
        campaign_dim_custom1,
        campaign_budget_total,
        COUNT(DISTINCT lineitem_id) as lineitem_count
    FROM {*}
    WHERE campaign_dim_custom1 IS NOT NULL
      AND meta_is_archived = FALSE
    GROUP BY campaign_name, campaign_dim_custom1, campaign_budget_total
    ORDER BY campaign_budget_total DESC
    """

    print(f"\nSQL Query:")
    print(query)

    df = manager.sql_query(query, return_dataframe=True)

    print(f"\n✓ Query returned {len(df)} campaigns with custom dimension 1")

    if len(df) > 0:
        print(f"\nFirst 3 results:")
        for idx, row in df.head(3).iterrows():
            print(f"  - Campaign: {row['campaign_name']}")
            print(f"    • Dimension: {row['campaign_dim_custom1']}")
            print(f"    • Budget: ${row['campaign_budget_total']:,.2f}")
            print(f"    • Line items: {int(row['lineitem_count'])}")

    print(f"\n✓ Successfully demonstrated simple SQL queries")


def complex_sql_queries(manager):
    """
    Demonstrate complex SQL queries for advanced analytics.

    Use Case:
        When you need sophisticated analysis:
        - Channel mix analysis (cost, impressions, CPM by channel)
        - Custom dimension analysis (budget by dimension)
        - KPI performance tracking
        - Multi-dimensional aggregations
        - Time-based analysis

    v3.0 Features:
        - Complex JOINs and aggregations
        - v3.0 metrics (impressions, clicks, reach, views)
        - v3.0 custom fields
        - Calculated fields (CPM, CTR, etc.)
        - Date functions and grouping

    Args:
        manager: Loaded WorkspaceManager instance

    Next Steps:
        - Build dashboards from results
        - Export to BI tools
        - Create automated reports
        - Combine with Python analysis
    """
    print("\n" + "="*60)
    print("Example 2: Complex SQL Queries")
    print("="*60)

    # ====================
    # QUERY 1: Channel mix analysis
    # ====================
    print(f"\n" + "-"*60)
    print("Query 1: Channel Mix Analysis")
    print("-"*60)

    query = """
    SELECT
        lineitem_channel,
        COUNT(DISTINCT lineitem_id) as lineitem_count,
        SUM(lineitem_cost_total) as total_cost,
        SUM(lineitem_metric_impressions) as total_impressions,
        SUM(lineitem_metric_clicks) as total_clicks,
        CASE
            WHEN SUM(lineitem_metric_impressions) > 0
            THEN (SUM(lineitem_cost_total) / SUM(lineitem_metric_impressions)) * 1000
            ELSE 0
        END as cpm,
        CASE
            WHEN SUM(lineitem_metric_impressions) > 0
            THEN (SUM(lineitem_metric_clicks) / SUM(lineitem_metric_impressions)) * 100
            ELSE 0
        END as ctr_percent
    FROM {*}
    WHERE lineitem_channel IS NOT NULL
      AND meta_is_archived = FALSE
      AND (is_placeholder = FALSE OR is_placeholder IS NULL)
    GROUP BY lineitem_channel
    ORDER BY total_cost DESC
    """

    print(f"\nSQL Query: Channel mix with CPM and CTR")

    df = manager.sql_query(query, return_dataframe=True)

    print(f"\n✓ Query returned {len(df)} channels")

    if len(df) > 0:
        print(f"\nChannel Mix:")
        for _, row in df.iterrows():
            print(f"  - {row['lineitem_channel']}:")
            print(f"    • Line items: {int(row['lineitem_count'])}")
            print(f"    • Total cost: ${row['total_cost']:,.2f}")
            if row['total_impressions'] > 0:
                print(f"    • Impressions: {row['total_impressions']:,.0f}")
                print(f"    • CPM: ${row['cpm']:.2f}")
            if row['total_clicks'] > 0:
                print(f"    • Clicks: {row['total_clicks']:,.0f}")
                print(f"    • CTR: {row['ctr_percent']:.2f}%")

    # ====================
    # QUERY 2: Custom dimension analysis
    # ====================
    print(f"\n" + "-"*60)
    print("Query 2: Custom Dimension Analysis")
    print("-"*60)

    query = """
    SELECT
        campaign_dim_custom1,
        COUNT(DISTINCT campaign_id) as campaign_count,
        COUNT(DISTINCT lineitem_id) as lineitem_count,
        SUM(lineitem_cost_total) as total_planned_cost
    FROM {*}
    WHERE campaign_dim_custom1 IS NOT NULL
      AND meta_is_archived = FALSE
      AND (is_placeholder = FALSE OR is_placeholder IS NULL)
    GROUP BY campaign_dim_custom1
    ORDER BY total_planned_cost DESC
    """

    print(f"\nSQL Query: Planned cost by custom dimension 1")

    df = manager.sql_query(query, return_dataframe=True)

    print(f"\n✓ Query returned {len(df)} custom dimension values")

    if len(df) > 0:
        print(f"\nBy Custom Dimension 1:")
        for _, row in df.iterrows():
            print(f"  - {row['campaign_dim_custom1']}:")
            print(f"    • Campaigns: {int(row['campaign_count'])}")
            print(f"    • Line items: {int(row['lineitem_count'])}")
            print(f"    • Total planned cost: ${row['total_planned_cost']:,.2f}")

    # ====================
    # QUERY 3: KPI performance analysis
    # ====================
    print(f"\n" + "-"*60)
    print("Query 3: KPI Performance Analysis")
    print("-"*60)

    query = """
    SELECT
        kpi_name,
        COUNT(DISTINCT campaign_id) as campaign_count,
        AVG(kpi_value) as avg_target,
        MIN(kpi_value) as min_target,
        MAX(kpi_value) as max_target
    FROM (
        SELECT DISTINCT
            campaign_id,
            campaign_kpi_name1 as kpi_name,
            campaign_kpi_value1 as kpi_value
        FROM {*}
        WHERE campaign_kpi_name1 IS NOT NULL
          AND meta_is_archived = FALSE
    )
    GROUP BY kpi_name
    ORDER BY campaign_count DESC
    """

    print(f"\nSQL Query: KPI performance at campaign level")

    df = manager.sql_query(query, return_dataframe=True)

    print(f"\n✓ Query returned {len(df)} KPIs")

    if len(df) > 0:
        print(f"\nKPI Analysis:")
        for _, row in df.iterrows():
            print(f"  - {row['kpi_name']}:")
            print(f"    • Campaigns using: {int(row['campaign_count'])}")
            print(f"    • Avg target: {row['avg_target']:.2f}")
            print(f"    • Range: {row['min_target']:.2f} - {row['max_target']:.2f}")

    # ====================
    # QUERY 4: Budget vs planned cost
    # ====================
    print(f"\n" + "-"*60)
    print("Query 4: Budget vs Planned Cost")
    print("-"*60)

    query = """
    SELECT
        meta_id,
        meta_name,
        AVG(campaign_budget_total) as campaign_budget,
        SUM(lineitem_cost_total) as planned_cost,
        AVG(campaign_budget_total) - SUM(lineitem_cost_total) as variance,
        CASE
            WHEN AVG(campaign_budget_total) > 0
            THEN (SUM(lineitem_cost_total) / AVG(campaign_budget_total)) * 100
            ELSE 0
        END as percent_planned
    FROM {*}
    WHERE meta_is_archived = FALSE
      AND (is_placeholder = FALSE OR is_placeholder IS NULL)
    GROUP BY meta_id, meta_name
    ORDER BY variance ASC
    """

    print(f"\nSQL Query: Budget vs planned cost at plan level")

    df = manager.sql_query(query, return_dataframe=True)

    print(f"\n✓ Query returned {len(df)} media plans")

    if len(df) > 0:
        print(f"\nBudget vs Planned (Top 3):")
        for _, row in df.head(3).iterrows():
            print(f"  - {row['meta_name']}:")
            print(f"    • Campaign budget: ${row['campaign_budget']:,.2f}")
            print(f"    • Planned cost: ${row['planned_cost']:,.2f}")
            print(f"    • Variance: ${row['variance']:,.2f}")
            print(f"    • % Planned: {row['percent_planned']:.1f}%")

    # ====================
    # QUERY 5: Time-based analysis
    # ====================
    print(f"\n" + "-"*60)
    print("Query 5: Time-Based Analysis")
    print("-"*60)

    query = """
    SELECT
        campaign_id,
        campaign_name,
        campaign_start_date,
        campaign_end_date,
        DATE_DIFF('day', campaign_start_date, campaign_end_date) as duration_days,
        AVG(campaign_budget_total) as campaign_budget,
        AVG(campaign_budget_total) / DATE_DIFF('day', campaign_start_date, campaign_end_date) as daily_budget
    FROM {*}
    WHERE campaign_start_date IS NOT NULL
      AND campaign_end_date IS NOT NULL
      AND meta_is_archived = FALSE
    GROUP BY campaign_id, campaign_name, campaign_start_date, campaign_end_date
    HAVING duration_days > 0
    ORDER BY daily_budget DESC
    """

    print(f"\nSQL Query: Campaign duration and daily budget at campaign level")

    df = manager.sql_query(query, return_dataframe=True)

    print(f"\n✓ Query returned {len(df)} campaigns")

    if len(df) > 0:
        print(f"\nTime-Based Analysis (Top 3):")
        for _, row in df.head(3).iterrows():
            print(f"  - {row['campaign_name']}:")
            print(f"    • Start: {row['campaign_start_date']}")
            print(f"    • End: {row['campaign_end_date']}")
            print(f"    • Duration: {int(row['duration_days'])} days")
            print(f"    • Campaign budget: ${row['campaign_budget']:,.2f}")
            print(f"    • Daily budget: ${row['daily_budget']:,.2f}")

    print(f"\n✓ Successfully demonstrated complex SQL queries")


if __name__ == "__main__":
    print("="*60)
    print("MediaPlanPy v3.0 - SQL Query Examples")
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
    simple_sql_queries(manager)

    complex_sql_queries(manager)

    print("\n" + "="*60)
    print("SQL Query Examples Completed!")
    print("="*60)

    print(f"\nWhat We Demonstrated:")
    print(f"  1. Simple SELECT queries with v3.0 fields")
    print(f"  2. Budget aggregation by objective")
    print(f"  3. Custom dimension filtering")
    print(f"  4. Channel mix analysis with CPM/CTR")
    print(f"  5. Custom dimension aggregation")
    print(f"  6. KPI performance tracking")
    print(f"  7. Budget vs actual variance")
    print(f"  8. Time-based analysis with date functions")

    print(f"\nNext Steps:")
    print(f"  - Create custom queries for your needs")
    print(f"  - Export results: df.to_csv('results.csv')")
    print(f"  - Build dashboards and reports")
    print(f"  - Combine with Python data processing")
    print(f"  - Use {{*}} or {{pattern}} for file pattern matching")
