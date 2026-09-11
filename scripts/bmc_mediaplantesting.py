
### Step 1: Import the Package

# Import Packages
import os
from pathlib import Path
from datetime import date, datetime
from decimal import Decimal

from mediaplanpy.workspace import WorkspaceManager
from mediaplanpy.models import MediaPlan

### Step 2: Initialize the Workspace Manager

# Initialize Workspace Manager
workspace = WorkspaceManager()


### Step 3: Create and Load a Workspace

# Create and Load a Workspace - I want to use the same one on my machine from example testing
# Create and Load a Workspace
# workspace_id, settings_file_path = workspace.create()
workspace_config = workspace.load(workspace_id="workspace_b92ee88b")
print(f"Workspace ID: {workspace_config["workspace_id"]}")
# print(f"Workspace Settings File Path: {workspace_config.settings_file_path}")

# Create a Media Plan (v3.0 schema)
media_plan = MediaPlan.create(
    created_by="brian.mcmanus@workconbrio.com",
    campaign_name="Summer 2025 Duff Beer Campaign",
    campaign_objective="Brand Awareness",
    campaign_start_date="2025-07-01",
    campaign_end_date="2025-09-30",
    campaign_budget=200000,
    # agency_id="A1",
    # agency_name="Example Agency",
    # advertiser_id="ADV1",
    # advertiser_name="Sample Advertiser",
    product_id="P1",
    product_name="Duff Beer",
    # campaign_type_id="C1",
    # campaign_type_name="Awareness",
    # v3.0: Use target_audiences array
    target_audiences=[{
        "name": "Adults 18-54",
        "demo_age_start": 21,
        "demo_age_end": 54,
        "demo_gender": "Any",
        "interest_attributes": "Adult Beer Drinkers"
    }],
    # v3.0: Use target_locations array
    target_locations=[{
        "name": "United States",
        "location_type": "Country",
        "location_list": ["USA"],
        
    },
    {
        "name": "Three Southeast States",
        "location_type": "State",
        "location_list": ["FL","GA","AL"],
        
    }],
    workflow_status_id="1",
    workflow_status_name="Planning",
    media_plan_name="BMc Test Plan",
    created_by_id="U123456",
    created_by_name="Brian McManus",
    comments="Initial version of media plan",
    is_current=True,
    is_archived=False,
    workspace_manager=workspace
)
print(f"Media Plan Created: {media_plan.meta.id}")


### Step 5: Add Line Items


# Add Line Items
lineitem = media_plan.create_lineitem({
    "name": "Search",
    "channel": "Search",
    "vehicle": "Google",
    "partner": "Google",
    "media_product": "Google Ads",
    "location_type": "Country",
    "location_name": "USA",
    "target_audience": "Adults 18-54",
    "adformat": "Text",
    "kpi": "Clicks",
    "cost_total": 5000,
    "cost_currency": "USD"
})
print(f"Line Item Created: {lineitem.id}")

# You can add as many line items as needed with different channels, costs, and configurations.

### Step 6: Save the Media Plan


# Save the Media Plan
saved_path = media_plan.save(workspace)
print(f"Media plan saved to: {saved_path}")

### Step 7: Run SQL Query to Get Total Spend

# Run SQL query for total spend
query = "SELECT SUM(lineitem_cost_total) AS total_spend FROM {*}"
result = workspace.sql_query(query)
print(result)


### Step 8: List All Saved Media Plans

# List saved media plans
plans = workspace.list_mediaplans()
for plan in plans:
    print(plan["meta_name"], plan["stat_total_cost"])


### Step 9: Export Plan to Excel

# Export media plan to Excel
media_plan.export_to_excel(
    workspace_manager=workspace,
    file_name="media_plan_export.xlsx",
    overwrite=True
)

### Step 10: Import Plan from Excel

# Import a new media plan from Excel

# imported_plan = MediaPlan.import_from_excel(
#     file_name="media_plan_export.xlsx",
#     workspace_manager=workspace
# )
# saved_path = imported_plan.save(workspace)
# print(f"Imported plan: {imported_plan.meta.id}")
