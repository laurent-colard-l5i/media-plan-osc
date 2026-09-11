"""
trace_mediaplan_history.py
--------------------------
Trace the version lineage of a media plan by its ID.

Usage:
    python scripts/trace_mediaplan_history.py <media_plan_id>

Example:
    python scripts/trace_mediaplan_history.py mediaplan_7695a631

What it does:
    1. Loads the workspace defined by WORKSPACE_ID below
    2. Looks up the given plan ID to find its campaign_id
    3. Fetches all versions of that campaign (same campaign_id)
    4. Builds and prints a lineage tree using parent_id relationships
    5. Flags which plan is current, which are archived, and the root plan
"""

import sys
from mediaplanpy.workspace import WorkspaceManager

# ── Configuration ─────────────────────────────────────────────────────────────
WORKSPACE_ID = "workspace_b92ee88b"   # Update this to match your workspace
# ──────────────────────────────────────────────────────────────────────────────


def load_workspace():
    manager = WorkspaceManager()
    try:
        manager.load(workspace_id=WORKSPACE_ID)
        print(f"✓ Workspace loaded: {WORKSPACE_ID}\n")
        return manager
    except Exception as e:
        print(f"✗ Could not load workspace '{WORKSPACE_ID}': {e}")
        print("  Update WORKSPACE_ID at the top of this script and re-run.")
        sys.exit(1)


def fetch_all_versions(manager, plan_id):
    """
    Given a plan ID, find its campaign_id then return all plans
    sharing that campaign_id, including archived ones.
    """
    # Step 1: find the target plan (include archived to cover all cases)
    lookup_query = f"""
    SELECT DISTINCT
        meta_id,
        meta_name,
        meta_parent_id,
        meta_is_current,
        meta_is_archived,
        meta_created_at,
        meta_comments,
        meta_created_by_name,
        campaign_id,
        campaign_name,
        campaign_budget_total
    FROM {{*}}
    WHERE meta_id = '{plan_id}'
    ORDER BY meta_created_at
    """
    try:
        result = manager.sql_query(lookup_query, return_dataframe=True)
    except Exception as e:
        print(f"✗ Query failed: {e}")
        sys.exit(1)

    if result.empty:
        print(f"✗ No plan found with ID '{plan_id}'.")
        print("  Check the ID and ensure the plan exists in this workspace.")
        sys.exit(1)

    row = result.iloc[0]
    campaign_id   = row["campaign_id"]
    campaign_name = row["campaign_name"]
    print(f"Campaign:  {campaign_name}")
    print(f"           {campaign_id}\n")

    # Step 2: fetch all plans under that campaign_id
    all_query = f"""
    SELECT DISTINCT
        meta_id,
        meta_name,
        meta_parent_id,
        meta_is_current,
        meta_is_archived,
        meta_created_at,
        meta_comments,
        meta_created_by_name,
        campaign_budget_total
    FROM {{*}}
    WHERE campaign_id = '{campaign_id}'
    ORDER BY meta_created_at
    """
    try:
        all_versions = manager.sql_query(all_query, return_dataframe=True)
    except Exception as e:
        print(f"✗ Failed to fetch campaign versions: {e}")
        sys.exit(1)

    return all_versions, campaign_id


def build_lineage_tree(df, target_id):
    """
    Build a dict of { parent_id -> [child rows] } and find root nodes.
    A root node has parent_id = None or a parent_id that doesn't exist
    in this dataset (external reference).
    """
    all_ids = set(df["meta_id"].tolist())
    children = {}   # parent_id -> list of row dicts
    roots    = []   # rows with no known parent

    for _, row in df.iterrows():
        pid = row.get("meta_parent_id")
        if pid and pid in all_ids:
            children.setdefault(pid, []).append(row)
        else:
            roots.append(row)

    # Sort children by creation date
    for pid in children:
        children[pid].sort(key=lambda r: r["meta_created_at"] or "")

    return roots, children


def format_row(row, target_id, prefix="", is_last=True):
    """Format a single plan row as a tree line."""
    mid      = row["meta_id"]
    name     = row["meta_name"] or "(unnamed)"
    created  = str(row["meta_created_at"])[:19] if row["meta_created_at"] else "unknown date"
    budget   = row["campaign_budget_total"]
    comments = row.get("meta_comments") or ""
    creator  = row.get("meta_created_by_name") or ""

    # Status tags
    tags = []
    if row.get("meta_is_current"):
        tags.append("CURRENT")
    if row.get("meta_is_archived"):
        tags.append("ARCHIVED")
    if mid == target_id:
        tags.append("← you are here")

    tag_str    = f"  [{', '.join(tags)}]" if tags else ""
    budget_str = f"  ${budget:,.2f}" if budget is not None else ""
    branch     = "└── " if is_last else "├── "
    line       = f"{prefix}{branch}{mid}"

    details = []
    details.append(f"{'':>{len(prefix) + 4}}  Name:    {name}{tag_str}")
    details.append(f"{'':>{len(prefix) + 4}}  Created: {created}{budget_str}")
    if creator:
        details.append(f"{'':>{len(prefix) + 4}}  By:      {creator}")
    if comments:
        details.append(f"{'':>{len(prefix) + 4}}  Note:    {comments[:80]}")

    return line, details


def print_tree(rows, children, target_id, prefix="", level=0):
    """Recursively print the lineage tree."""
    for i, row in enumerate(rows):
        is_last   = (i == len(rows) - 1)
        mid       = row["meta_id"]
        line, details = format_row(row, target_id, prefix, is_last)

        print(line)
        for d in details:
            print(d)
        print()

        # Recurse into children
        if mid in children:
            next_prefix = prefix + ("    " if is_last else "│   ")
            print_tree(children[mid], children, target_id, next_prefix, level + 1)


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/trace_mediaplan_history.py <media_plan_id>")
        print("Example: python scripts/trace_mediaplan_history.py mediaplan_7695a631")
        sys.exit(1)

    target_id = sys.argv[1].strip()
    print("=" * 60)
    print("  Media Plan Lineage Tracer")
    print("=" * 60)
    print(f"  Tracing: {target_id}\n")

    manager     = load_workspace()
    df, _       = fetch_all_versions(manager, target_id)
    roots, children = build_lineage_tree(df, target_id)

    total   = len(df)
    current = df[df["meta_is_current"] == True]
    archived = df[df["meta_is_archived"] == True]

    print(f"Found {total} version(s) total  ·  "
          f"{len(current)} current  ·  {len(archived)} archived\n")
    print("-" * 60)
    print("Lineage Tree (oldest → newest)\n")

    print_tree(roots, children, target_id)

    print("-" * 60)
    print("Done.\n")


if __name__ == "__main__":
    main()
