"""
Create Media Plan: BMc Test Campaign Q2 2026
============================================
Uses the MediaPlanPy SDK v3.0 to create a multi-channel media plan
with line items across Paid Social, Video/CTV, and Programmatic Display.

Campaign Details:
    - Name:         BMc Test Campaign Q2 2026
    - Date Range:   2026-04-01 to 2026-06-30
    - Total Budget: $200,000
    - Created By:   BMc with Claude Cowork

How to Run (Windows):
    python create_bmc_q2_2026_plan.py

Prerequisites:
    - MediaPlanPy SDK installed:  pip install -e .
    - An existing workspace configured at C:/mediaplanpy/
      To find your workspace ID, check: C:/mediaplanpy/ for files named
      like "workspace_XXXXXXXX_settings.json" — the XXXXXXXX part is the ID.
"""

from decimal import Decimal
from mediaplanpy.workspace import WorkspaceManager
from mediaplanpy.models import MediaPlan


# ============================================================================
# CONFIGURATION — update WORKSPACE_ID before running
# ============================================================================

# Your workspace ID — find it at C:/mediaplanpy/<workspace_id>_settings.json
# Example: if the file is "workspace_b92ee88b_settings.json", set:
#          WORKSPACE_ID = "workspace_b92ee88b"
WORKSPACE_ID = "workspace_b92ee88b"

# ============================================================================
# CAMPAIGN & LINE ITEM DETAILS
# ============================================================================

CAMPAIGN_NAME       = "BMc Test Campaign Q2 2026"
MEDIA_PLAN_NAME     = "BMc Test Campaign Q2 2026"
START_DATE          = "2026-04-01"
END_DATE            = "2026-06-30"
TOTAL_BUDGET        = Decimal("200000.00")
CREATED_BY          = "BMc with Claude Cowork"
CAMPAIGN_OBJECTIVE  = "awareness"   # e.g. awareness, consideration, conversion

# Line items — channel, ad format, and budget allocation
# Channels and adformat are free text; edit to match your naming conventions.
# Budgets here sum to TOTAL_BUDGET ($200,000). Adjust as needed.
LINE_ITEMS = [
    # --- Paid Social ---
    {
        "name":        "Paid Social - Meta Feed Ads",
        "channel":     "Paid Social",
        "adformat":    "Feed Ads",
        "start_date":  START_DATE,
        "end_date":    END_DATE,
        "cost_total":  Decimal("55000.00"),
    },
    {
        "name":        "Paid Social - LinkedIn Sponsored Content",
        "channel":     "Paid Social",
        "adformat":    "Sponsored Content",
        "start_date":  START_DATE,
        "end_date":    END_DATE,
        "cost_total":  Decimal("45000.00"),
    },
    {
        "name":        "Paid Social - TikTok In-Feed Video",
        "channel":     "Paid Social",
        "adformat":    "In-Feed Video",
        "start_date":  START_DATE,
        "end_date":    END_DATE,
        "cost_total":  Decimal("30000.00"),
    },
    # --- Video / CTV ---
    {
        "name":        "Video - Pre-Roll",
        "channel":     "Video",
        "adformat":    "Pre-Roll",
        "start_date":  START_DATE,
        "end_date":    END_DATE,
        "cost_total":  Decimal("40000.00"),
    },
    {
        "name":        "Video - Connected TV",
        "channel":     "Video",
        "adformat":    "Connected TV",
        "start_date":  START_DATE,
        "end_date":    END_DATE,
        "cost_total":  Decimal("15000.00"),
    },
    # --- Programmatic Display ---
    {
        "name":        "Programmatic Display",
        "channel":     "Display",
        "adformat":    "Programmatic",
        "start_date":  START_DATE,
        "end_date":    END_DATE,
        "cost_total":  Decimal("15000.00"),
    },
]


# ============================================================================
# MAIN
# ============================================================================

def main():
    # --- Validate workspace ID is set ---
    if "YOUR_WORKSPACE_ID_HERE" in WORKSPACE_ID:
        print("ERROR: Please set WORKSPACE_ID at the top of this script.")
        print("  Check C:/mediaplanpy/ for files like 'workspace_XXXXXXXX_settings.json'")
        print("  and set WORKSPACE_ID = 'workspace_XXXXXXXX'")
        return

    # --- Validate budget ---
    line_item_total = sum(li["cost_total"] for li in LINE_ITEMS)
    if line_item_total != TOTAL_BUDGET:
        print(f"WARNING: Line item costs sum to ${line_item_total:,.2f}, "
              f"but TOTAL_BUDGET is ${TOTAL_BUDGET:,.2f}.")
        print("  Update LINE_ITEMS budgets or TOTAL_BUDGET before saving.")

    # --- Load workspace ---
    print(f"\nLoading workspace: {WORKSPACE_ID}")
    manager = WorkspaceManager()
    manager.load(workspace_id=WORKSPACE_ID)
    print("  ✓ Workspace loaded")

    # --- Create media plan ---
    print(f"\nCreating media plan: {MEDIA_PLAN_NAME}")
    plan = MediaPlan.create(
        campaign_name=CAMPAIGN_NAME,
        media_plan_name=MEDIA_PLAN_NAME,
        campaign_start_date=START_DATE,
        campaign_end_date=END_DATE,
        campaign_budget_total=TOTAL_BUDGET,
        campaign_objective=CAMPAIGN_OBJECTIVE,
        created_by_name=CREATED_BY,
        lineitems=LINE_ITEMS,
    )
    print("  ✓ Media plan created")

    # --- Print summary ---
    print(f"\n{'='*55}")
    print(f"  Media Plan Summary")
    print(f"{'='*55}")
    print(f"  Plan ID:     {plan.meta.id}")
    print(f"  Plan Name:   {plan.meta.name}")
    print(f"  Campaign:    {plan.campaign.name}")
    print(f"  Period:      {plan.campaign.start_date} → {plan.campaign.end_date}")
    print(f"  Budget:      ${plan.campaign.budget_total:,.2f}")
    print(f"  Line Items:  {len(plan.lineitems)}")
    print(f"\n  Line Item Breakdown:")
    channel_totals = {}
    for li in plan.lineitems:
        ch = li.channel or "Unassigned"
        channel_totals[ch] = channel_totals.get(ch, Decimal("0")) + (li.cost_total or Decimal("0"))
        print(f"    • {li.name:<45} ${li.cost_total:>10,.2f}")
    print(f"\n  By Channel:")
    for ch, total in channel_totals.items():
        print(f"    {ch:<20} ${total:>10,.2f}")
    print(f"  {'─'*35}")
    print(f"  {'TOTAL':<20} ${sum(channel_totals.values()):>10,.2f}")
    print(f"{'='*55}")

    # --- Save ---
    print(f"\nSaving media plan to workspace...")
    saved_path = plan.save(manager)
    print(f"  ✓ Saved: {saved_path}")

    print(f"\nDone! Media Plan ID: {plan.meta.id}")
    print(f"Next steps:")
    print(f"  - Load:   manager.load_mediaplan('{plan.meta.id}')")
    print(f"  - Export: see examples/examples_06_export_mediaplan.py")


if __name__ == "__main__":
    main()
