# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Testing
- Run all tests: `pytest`
- Run specific test file: `pytest tests/test_models.py`
- Run with coverage: `pytest --cov=mediaplanpy`

### Code Quality
- Format code: `black src/ tests/`
- Sort imports: `isort src/ tests/`
- Type checking: `mypy src/mediaplanpy`
- Install dev dependencies: `pip install -e ".[dev]"`

### Build & Install
- Install package in development mode: `pip install -e .`
- Build package: `python -m build`

### CLI Usage
- Access CLI: `mediaplanpy --help`
- The CLI entry point is in `src/mediaplanpy/cli.py`

## Architecture Overview

MediaPlanPy is a Python SDK for working with media plans that follow the MediaPlan Schema standard. The codebase is organized into several key modules:

### Core Components

**Models (`src/mediaplanpy/models/`)**
- `MediaPlan`: Main model representing a complete media plan with campaigns and line items
- `Campaign`: Represents a campaign with budget and target audience information
- `LineItem`: Individual line items within campaigns with metrics and cost data
- `TargetAudience`: New v3.0 model for audience arrays with 13+ attributes
- `TargetLocation`: New v3.0 model for location arrays with multiple targeting options
- `MetricFormula`: New v3.0 model for calculated metric formulas
- All models inherit from `BaseModel` and use Pydantic for validation
- Models support schema v3.0 with v2.0 migration capability

**Schema Management (`src/mediaplanpy/schema/`)**
- Version-aware schema validation and migration system
- Supports schema version 3.0 with v2.0 migration support (v0.0 and v1.0 no longer supported)
- `SchemaValidator`: Validates media plans against schemas
- `SchemaMigrator`: Migrates v2.0 → v3.0 with automatic audience/location restructuring
- `SchemaRegistry`: Manages schema definitions stored in `definitions/` subdirectories
- `refs.py` + `get_schema()`/`get_schema_bundle()`/`get_example()` (v3.0.10): serve those
  definitions to outside consumers — see "Schema Exposure" below

**Storage (`src/mediaplanpy/storage/`)**
- Pluggable storage backends: Local filesystem, S3, Google Drive, PostgreSQL
- Format handlers for JSON, Excel, and Parquet files
- `read_mediaplan()` and `write_mediaplan()` are the main entry points
- Storage configuration is managed through workspace settings
- `get_storage_backend()` caches and reuses backend instances (v3.0.12) - see "Storage
  Backend Caching" below before adding a new call site or a new backend type

**Workspace Management (`src/mediaplanpy/workspace/`)**
- Multi-environment configuration system
- Workspace configurations define storage locations and database connections
- Query functionality across multiple media plans within a workspace
- Workspace validation against JSON schemas

**Excel Integration (`src/mediaplanpy/excel/`)**
- Import/export functionality for Excel files
- Template-based Excel generation
- Excel validation against schema requirements
- Custom formatting and style handling

### Key Patterns

**Schema Versioning**
- The system supports schema version 3.0 as current, with v2.0 migration support
- Version detection is automatic from media plan metadata
- v2.0 → v3.0 migration handles audience/location restructuring and new field additions
- v0.0 and v1.0 are no longer supported

**Schema Exposure (v3.0.10)**
- `schema.get_schema()` returns a **self-contained** document. The on-disk
  `mediaplan.schema.json` references its siblings by bare filename
  (`{"$ref": "campaign.schema.json"}`) — a convention of this package's own
  `definitions/<version>/` layout that no outside consumer can dereference. Resolution lives
  in `schema/refs.py` for that reason: re-implementing it elsewhere breaks silently the first
  time these files are reorganised.
- External (filename) references are **inlined**; local `#/$defs/...` pointers are **hoisted**
  into the result's own `$defs` and retargeted, not expanded. `dictionary.schema.json` shares
  one definition across ~35 custom-field slots, so expanding in place takes the media plan
  schema from ~32 KB to ~92 KB. `inline_local=True` still offers full expansion. Hoisted names
  are namespaced by source document (`dictionary__custom_field_config`) so merging documents
  cannot let one definition shadow another.
- The property consumers rely on is `contains_external_ref()` — "points at nothing you cannot
  reach" — not a blanket "no `$ref` anywhere".
- `get_example()` **generates** its example via `MediaPlan.create()` rather than returning a
  fixture, so it cannot drift from the schema. Do not replace it with a stored file.
- Primary consumer: `planmatic_ask_api` re-serves these over HTTP (`GET /schemas/{entity_type}`),
  which `planmatic_mcp` proxies as its `entity_schema` tool.

**Id generation on import**
- `_ensure_entity_ids()` in `models/mediaplan_json.py` mints `meta.id`, `campaign.id` and each
  `lineitems[].id` when absent, matching `MediaPlan.create()`, `create_lineitem()` and the Excel
  importer. Before v3.0.10 only `meta.id` was minted, so an identical plan imported as Excel and
  failed as JSON.
- Ids are filled **only when absent**, which is what makes export → edit → re-import safe.
- This is on the **JSON import path only**. `MediaPlan.from_dict()` still requires all three, and
  `schema.validate()` still reports them missing — it validates a document literally. Both are
  defensible (they answer different questions) but the asymmetry surprises people; keep it in
  mind before documenting ids as simply "optional".

**Campaigns Are Derived, Not Stored**
- There is no campaign file, no campaign record, and no stored campaign state.
  `WorkspaceManager.list_campaigns()` (`workspace/query.py`) derives its rows entirely
  from media plan files: it filters archived *plans* out at the SQL level, then keeps
  one row per `campaign_id` taken from that campaign's current/latest plan.
- Consequences, all load-bearing: a campaign is "archived" exactly when **every** one
  of its plans is archived (archiving some leaves the campaign fully visible from a
  survivor); a campaign ceases to exist when its last plan is deleted; and every
  campaign lifecycle operation is therefore a **cascade over plans**.
- `WorkspaceManager.archive_campaign()` / `restore_campaign()` / `delete_campaign()`
  (`workspace/campaign_lifecycle.py`, v3.0.11) implement that cascade. They are
  non-atomic and continue-on-error, returning `plans_changed`/`plans_skipped`/
  `plans_failed` rather than hiding a partial result.
- This is not an implementation shortcut — it is the only semantics the storage model
  can express. Do not "fix" it by inventing a campaign record.

**Storage Backend Caching (v3.0.12)**
- `get_storage_backend()` used to construct a brand-new backend on every call.
  `LocalStorageBackend.__init__` is free (just path resolution), but
  `S3StorageBackend.__init__` builds a boto3 client and performs a live
  `head_bucket()` connectivity check - a real network round-trip. Several
  downstream packages call `get_storage_backend()` many times per logical
  operation (every settings read/write, every entity reload), so each one paid
  for the same connectivity check repeatedly within a single request.
- The cache lives in `mediaplanpy/storage/__init__.py`, module-level (not on
  `WorkspaceManager`), because every known caller constructs a fresh
  `WorkspaceManager` and a fresh resolved-config dict per call - an
  instance-scoped or identity-keyed cache would never hit in practice.
- **Cache key is content, not identity or `workspace_id` alone**: `(workspace_id,
  mode, json.dumps(storage_config[mode], sort_keys=True))`. `workspace_id` is
  included even though it lives outside `storage.*` because `S3StorageBackend`
  defaults its `prefix` to `workspace_id` when `storage.s3.prefix` is unset -
  two workspaces with identical `storage.s3` blocks but different ids must not
  share a backend. If a backend class is added whose behavior depends on a
  config field outside `storage.<mode>` and `workspace_id`, the cache key must
  be extended to cover it or that field will be silently ignored for caching
  purposes - this is the one thing to check before adding a new backend type.
- Bounded + LRU (`_BACKEND_CACHE_MAXSIZE`, default 64) so a long-running
  multi-tenant server can't grow this cache without limit. A failed
  construction is never cached - the next call retries from scratch.
- `clear_storage_backend_cache()` forces fresh instances process-wide. Needed
  after rotating credentials a cached backend has no way to notice on its own
  (static env-var credentials aren't re-read after client construction;
  profile- and IAM-role-based credentials refresh themselves and don't need
  this).

**Database Integration**
- PostgreSQL integration is optional (requires `psycopg2-binary`)
- Database functionality is patched into MediaPlan models when available
- Use `is_database_available()` to check if database features are accessible

**Error Handling**
- Custom exception hierarchy in `exceptions.py`
- All exceptions inherit from `MediaPlanError`
- Specific exceptions for schema, storage, validation, and workspace errors

## Configuration

**Version Information**
- Current SDK version: 3.0.12
- Current schema version: 3.0
- Supported major versions: [2, 3]

**Dependencies**
- Core: pydantic, pandas, jsonschema
- Optional: openpyxl (Excel), psycopg2-binary (PostgreSQL), pyarrow (Parquet), boto3 (S3)
- All dependencies are listed in `pyproject.toml`

## Testing Notes

- Tests are in `tests/` directory using pytest
- Test files follow `test_*.py` naming convention
- Tests cover models, schema validation, storage backends, Excel functionality, and workspace management
- Use `pytest tests/test_specific.py::TestClass::test_method` to run individual tests