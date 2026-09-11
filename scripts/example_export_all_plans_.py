"""
Claude Cowork generated 2026-03-16
export_all_to_excel.py

Export all media plans in a workspace to Excel files.

Usage:
    python export_all_to_excel.py --workspace path/to/workspace.json
    python export_all_to_excel.py --workspace path/to/workspace.json --campaign-id camp_abc123
    python export_all_to_excel.py --workspace path/to/workspace.json --current-only
    python export_all_to_excel.py --workspace path/to/workspace.json --output-dir ./my_exports
    python export_all_to_excel.py --workspace path/to/workspace.json --overwrite
"""

import argparse
import logging
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Export all media plans in a workspace to Excel files."
    )
    parser.add_argument(
        "--workspace",
        required=True,
        metavar="PATH",
        help="Path to the workspace JSON configuration file.",
    )
    parser.add_argument(
        "--campaign-id",
        metavar="ID",
        help="Only export media plans that belong to this campaign ID.",
    )
    parser.add_argument(
        "--current-only",
        action="store_true",
        help="Only export media plans flagged as is_current=True.",
    )
    parser.add_argument(
        "--output-dir",
        metavar="DIR",
        help=(
            "Local directory to write Excel files to instead of the workspace "
            "exports folder.  The directory will be created if it does not exist."
        ),
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing Excel files. Default is to skip files that already exist.",
    )
    parser.add_argument(
        "--no-docs",
        action="store_true",
        help="Omit the Documentation sheet from exported Excel files.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable DEBUG-level logging.",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # ------------------------------------------------------------------
    # Import mediaplanpy (give a clean error if it is not installed)
    # ------------------------------------------------------------------
    try:
        from mediaplanpy.workspace import WorkspaceManager
        from mediaplanpy.models import MediaPlan
    except ImportError as exc:
        logger.error(
            "Could not import mediaplanpy. "
            "Make sure the package is installed: pip install -e ."
        )
        logger.error(str(exc))
        sys.exit(1)

    # ------------------------------------------------------------------
    # Load workspace
    # ------------------------------------------------------------------
    workspace_path = Path(args.workspace).resolve()
    if not workspace_path.exists():
        logger.error("Workspace file not found: %s", workspace_path)
        sys.exit(1)

    logger.info("Loading workspace: %s", workspace_path)
    manager = WorkspaceManager()
    try:
        manager.load(workspace_path=str(workspace_path))
    except Exception as exc:
        logger.error("Failed to load workspace: %s", exc)
        sys.exit(1)

    # ------------------------------------------------------------------
    # Build filters
    # ------------------------------------------------------------------
    filters = {}
    if args.campaign_id:
        filters["campaign_id"] = args.campaign_id
        logger.info("Filtering to campaign_id = %s", args.campaign_id)
    if args.current_only:
        filters["meta_is_current"] = True
        logger.info("Filtering to current media plans only (is_current=True)")

    # ------------------------------------------------------------------
    # List media plans
    # ------------------------------------------------------------------
    logger.info("Querying workspace for media plans…")
    try:
        plan_records = manager.list_mediaplans(
            filters=filters if filters else None,
            include_stats=False,
        )
    except Exception as exc:
        logger.error("Failed to list media plans: %s", exc)
        sys.exit(1)

    if not plan_records:
        logger.warning("No media plans found in workspace (with current filters).")
        sys.exit(0)

    logger.info("Found %d media plan(s) to export.", len(plan_records))

    # ------------------------------------------------------------------
    # Validate / prepare optional local output directory
    # ------------------------------------------------------------------
    output_dir = None
    if args.output_dir:
        output_dir = Path(args.output_dir).resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Writing Excel files to local directory: %s", output_dir)

    # ------------------------------------------------------------------
    # Export loop
    # ------------------------------------------------------------------
    success_count = 0
    skip_count = 0
    error_count = 0

    for idx, record in enumerate(plan_records, start=1):
        plan_id = record.get("meta_id")
        plan_name = record.get("meta_name") or plan_id
        campaign_name = record.get("campaign_name") or record.get("campaign_id", "unknown_campaign")

        logger.info(
            "[%d/%d] Processing: %s  (campaign: %s)",
            idx, len(plan_records), plan_name, campaign_name,
        )

        if not plan_id:
            logger.warning("  Skipping record with no meta_id: %s", record)
            skip_count += 1
            continue

        # Build Excel file name
        safe_name = plan_id.replace("/", "_").replace("\\", "_")
        file_name = f"{safe_name}.xlsx"

        # If a local output directory is specified, check for an existing file there
        if output_dir:
            target_path = output_dir / file_name
            if target_path.exists() and not args.overwrite:
                logger.info("  Skipping (already exists): %s", target_path)
                skip_count += 1
                continue

        # Load the full media plan
        try:
            plan = MediaPlan.load(
                workspace_manager=manager,
                media_plan_id=plan_id,
            )
        except Exception as exc:
            logger.error("  Failed to load media plan '%s': %s", plan_id, exc)
            error_count += 1
            continue

        # Export to Excel
        try:
            if output_dir:
                # Export directly to the local directory
                exported_path = plan.export_to_excel(
                    file_path=str(target_path),
                    include_documentation=not args.no_docs,
                    overwrite=args.overwrite,
                )
            else:
                # Export to the workspace exports folder
                exported_path = plan.export_to_excel(
                    workspace_manager=manager,
                    file_name=file_name,
                    include_documentation=not args.no_docs,
                    overwrite=args.overwrite,
                )
            logger.info("  Exported: %s", exported_path)
            success_count += 1

        except Exception as exc:
            logger.error("  Failed to export '%s': %s", plan_id, exc)
            error_count += 1

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    logger.info("=" * 60)
    logger.info(
        "Export complete.  Success: %d  |  Skipped: %d  |  Errors: %d",
        success_count, skip_count, error_count,
    )
    if error_count:
        sys.exit(1)


if __name__ == "__main__":
    main()