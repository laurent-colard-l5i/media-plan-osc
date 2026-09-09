# Changelog

## [v3.0.12] - 2026-09-09

### Changed
- **Performance: `get_storage_backend()` now caches and reuses backend instances**
  instead of constructing a new one on every call.

  `LocalStorageBackend.__init__()` is essentially free (path resolution only), but
  `S3StorageBackend.__init__()` builds a boto3 client and performs a live
  `head_bucket()` connectivity check against the configured bucket - a real network
  round-trip. Several downstream packages call `get_storage_backend()` many times
  per logical operation (once per settings read, write, or existence check, and
  again on every entity reload within a multi-step workflow), so each one was
  paying for the same connectivity check repeatedly within a single request or
  automation run. Observed in practice via `planmatic_datamart`: a single
  extract-transform-load pass over one file against an S3-backed workspace
  triggered roughly 30 backend constructions, each with its own `head_bucket()`
  round-trip.

  The cache is keyed by content - `(workspace_id, mode, json.dumps(the
  mode-specific storage config, sort_keys=True))` - not by `workspace_config`'s
  object identity and not by `workspace_id` alone. Every known caller constructs a
  fresh `WorkspaceManager` and a fresh resolved-config dict per call, so an
  identity-keyed cache would never hit in practice; and `S3StorageBackend` defaults
  its `prefix` to `workspace_id` when `storage.s3.prefix` is unset, so two
  workspaces with identical `storage.s3` blocks but different ids must not be
  allowed to share a backend (or one workspace's writes could land in another's S3
  prefix). This is the property the new unit tests in
  `tests/unit/test_storage_backend_cache.py` check directly.

  The cache is bounded and LRU (`_BACKEND_CACHE_MAXSIZE`, default 64 distinct
  configurations) so a long-running, multi-tenant process cannot grow it without
  limit, and a failed backend construction is never cached - the next call for
  that configuration retries from scratch rather than replaying the failure.

  One deliberate, documented behavior change: `S3StorageBackend`'s connectivity
  check previously ran on every call to `get_storage_backend()`, so a bucket
  becoming unreachable mid-process would surface immediately at the next call. It
  now only runs when a configuration is first constructed (a cache miss); after
  that, a connectivity problem surfaces at the next actual `read_file`/`write_file`
  call instead of at `get_storage_backend()` itself. New `clear_storage_backend_cache()`
  forces fresh backends process-wide when needed - most notably after rotating
  credentials that a cached backend has no way to notice on its own (static
  `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY` env vars are read once at client
  construction and not re-read afterward; profile- and IAM-role-based credentials
  refresh themselves via boto3 and do not need this).

  Purely additive/non-breaking: no consumer inspected holds a backend across calls
  or relies on `get_storage_backend()` returning a distinct instance each time, and
  bad configuration still raises `StorageError` synchronously on first use.

## [v3.0.11] - 2026-09-04

### Added
- Campaign lifecycle methods on `WorkspaceManager`: `archive_campaign()`,
  `restore_campaign()` and `delete_campaign()`.

  Campaigns have no independent existence in this data model. There is no campaign
  file and no campaign record: `list_campaigns()` derives its rows entirely from
  media plan files, keeping one row per `campaign_id` after archived *plans* have
  been filtered out at the SQL level. A campaign is therefore "archived" exactly
  when every one of its plans is, and it ceases to exist when its last plan is
  deleted. Every one of these methods is consequently a cascade over the campaign's
  media plans rather than a state transition on a campaign - not an implementation
  shortcut, but the only semantics the storage model can express.

  `archive_campaign()` archives all plans including the current one, via
  `MediaPlan.archive(allow_current=True)` - the parameter added in 3.0.5 for exactly
  this case, which preserves `is_current` rather than clearing it, so a later restore
  reinstates the same current plan with no re-election step.

  All three are non-atomic and continue-on-error: there is no transaction spanning
  file storage, Parquet and PostgreSQL, so one plan failing does not abandon the
  rest. Each returns `plans_changed` / `plans_skipped` / `plans_failed` and sets
  `success=False` if anything failed, rather than hiding a partial cascade. Re-running
  after a partial failure is safe - an already-archived plan is skipped, not errored.

  `delete_campaign()`'s outcome fields differ by mode, so that no field name
  claims something happened when it did not. A dry run reports `plans_to_delete`
  (the intent) and `files_to_delete`, and omits `plans_changed`/`deleted_files`
  entirely; a real delete reports `plans_changed` and `deleted_files` and omits
  `files_to_delete`. This matters because `plans_changed` means "ids actually
  transitioned" in `archive_campaign()`/`restore_campaign()` -- sharing it with a
  preview would have let a caller reading it consistently conclude that a dry run
  had already deleted the campaign. On a dry run, "previewed cleanly" is
  `plans_to_delete` minus `plans_failed`.

  Two deliberate asymmetries with the plan-level methods, both documented in the
  docstrings so neither reads as an oversight:
  - `delete_campaign()` defaults `dry_run=True`, where `MediaPlan.delete()` defaults
    it to `False`. The cascade is N times more destructive and this is new API with
    no backwards-compatibility obligation to the riskier default.
  - `delete_campaign()` has no `allow_current_plan_deletion` parameter. Deleting a
    campaign means deleting its current plan too; a guard against that would make the
    method impossible to complete.

  `restore_campaign()` un-archives **every** archived plan in the campaign, not only
  those a previous `archive_campaign()` archived. Nothing in the data model records
  why a plan was archived, so a plan archived individually beforehand is restored too.
  This is an accepted tradeoff taken over adding a provenance field to the schema;
  callers needing a precise inverse should persist `archive_campaign()`'s
  `plans_changed` list and restore those plans individually via `MediaPlan.restore()`.

- `CampaignNotFoundError`, raised when a campaign lifecycle method is given a
  `campaign_id` no media plan carries. Kept distinct from `StorageError` (the same
  reasoning as 3.0.7's `MediaPlanNotFoundError`) so consumers can map it to a 404
  without string-matching a message.

### Notes
- Purely additive. No existing method changes shape or behaviour.
- Deliberately **not** added: `Campaign.archive()`/`.restore()`/`.delete()` instance
  methods (`Campaign` is a nested sub-model of `MediaPlan` with no storage identity
  or `WorkspaceManager` reference - giving it a lifecycle would mean inventing both);
  a campaign `set_as_current` (a campaign has no current-ness - its plans elect one
  among themselves); and CLI commands (there are no `mediaplan archive` CLI commands
  either, so adding campaign ones would make campaign lifecycle more discoverable
  from the CLI than plan lifecycle).

---

## [v3.0.10] - 2026-09-04

### Added
- Public schema access: `schema.get_schema()`, `schema.get_schema_bundle()`,
  `schema.get_example()`
  These schemas ship with this package, so this package now serves them. The
  immediate consumer is `planmatic_ask_api`, which re-serves them over HTTP so
  an LLM agent can author a media plan from scratch rather than copying an
  existing one; SDK users get the same access without an API in the loop.

  `get_schema()` returns a **self-contained** document by default. That matters
  because `mediaplan.schema.json` references its siblings by bare filename
  (`{"$ref": "campaign.schema.json"}`) - a convention of this package's own
  `definitions/` layout that no outside consumer can dereference, and that
  every outside consumer would otherwise have to re-implement and keep in step
  with. Resolution lives in the new `schema/refs.py`.

  External (filename) references are **inlined**; local `#/$defs/...` pointers
  are **hoisted** into the result's own `$defs` and rewritten, not expanded in
  place. Expanding them is available via `inline_local=True` but is not the
  default: `dictionary.schema.json` shares one definition across ~35
  custom-field slots, and inlining it at every site takes the resolved media
  plan schema from ~32 KB to ~92 KB, for a consumer that pays per byte of
  context. Hoisted definitions are namespaced by source document
  (`dictionary__custom_field_config`) so that merging several documents cannot
  let one definition quietly shadow another, and definitions nothing reaches
  are dropped.

  `get_example()` **generates** a minimal valid media plan via
  `MediaPlan.create()` rather than returning a stored fixture, so the example
  cannot drift out of sync with the schema - both come from this library at
  this version.

- `examples/examples_16_schemas.py` - worked demonstration of the above. Steps 1-3
  and 6 run with no workspace at all, since the schemas ship with the SDK.

### Fixed
- JSON import now auto-generates `campaign.id` and line item ids, not just
  `meta.id`
  `MediaPlan.create()`, `create_lineitem()` and the Excel importer all minted
  all three ids when absent; the JSON importer minted only `meta.id`. The same
  plan therefore imported cleanly as Excel and failed as JSON, on ids that the
  schema marks required but that no caller has a reason to invent. The
  asymmetry was an incomplete implementation rather than a design choice - the
  helper's own docstring described it as mirroring the Excel importer, which it
  did for one field of three.

  `_ensure_meta_id()` becomes `_ensure_entity_ids()` (the old name is retained
  as an alias). Ids are filled in **only when absent**, so an export -> edit ->
  re-import round trip preserves every id it was given, exactly as `meta.id`
  always has. A plan with no `campaign` block at all is left untouched, so the
  validator still reports that as the schema violation it is instead of it
  being masked by an invented campaign.

  **Scope worth knowing:** the minting is on the JSON *import* path.
  `MediaPlan.from_dict()` builds a model directly and still requires all three
  ids, and `schema.validate()` still reports them missing, since it validates a
  document literally. Both are defensible - they answer different questions from
  "can this be imported?" - but the asymmetry is easy to trip over when reading
  "ids are optional" unqualified. Documented in `SDK_REFERENCE.md` and
  demonstrated in `examples_16_schemas.py` step 5.

---

## [v3.0.9] - 2026-08-26

### Fixed
- Excel export crash caused by tz-aware `Meta.created_at` (3.0.8 regression)
  3.0.8 made `Meta.created_at` tz-aware (`datetime.now(timezone.utc)`) to fix a
  real UTC-skew bug - the correct instant, but openpyxl rejects tz-aware
  datetimes outright ("Excel does not support timezones in datetimes"), and
  the metadata sheet wrote `meta.created_at` directly into a cell as a native
  datetime object, crashing every `export_to_excel()` call. The exporter now
  strips `tzinfo` before writing the cell - Excel has no timezone concept for
  datetime cells anyway, so nothing the file format could represent is lost;
  the written value is still the correct UTC instant, just without the
  Python-level tz marker. The importer reattaches `timezone.utc` when reading
  a naive datetime back from that cell, so an export/reimport round-trip
  doesn't quietly regress to an ambiguous naive timestamp - the same failure
  mode 3.0.8's fix addressed in the first place.

---

## [v3.0.8] - 2026-08-18

### Fixed
- `Meta.created_at` stamped with UTC instead of naive local time
  Both the Pydantic field default and every save()/create()/Excel-import site
  that stamps `meta.created_at` used naive `datetime.now()` - local server
  wall-clock time with no timezone info. Downstream consumers reading or
  displaying the field as UTC saw a reproducible skew equal to the server's
  UTC offset (e.g. a plan created at 23:33:24 on a UTC-4 server recorded
  19:33:23). All five sites that set `meta.created_at` (the `Meta` model's
  field default, `MediaPlan.create()`, `MediaPlan.save()`'s first-save
  timestamp, and both Excel-import fallbacks) now use
  `datetime.now(timezone.utc)`. Already-persisted (skewed) values are left as
  historical data - a separate product decision, not part of this code fix.
- `{regex}` filter with `|` alternation silently returning 0 rows
  `_build_sql_filter_conditions()`'s regex branch ran the pattern through the
  generic literal-value sanitizer (`_escape_sql_value()`) before converting it
  to a SQL `LIKE` pattern. That sanitizer's whitelist strips anything that
  isn't alphanumeric/space/`-`/`.`/`:`/`@` - so a pattern like
  `"Meridian|PROC|QA"` had its `|` characters silently removed, becoming
  `"MeridianPROCQA"`, wrapped as `LIKE '%MeridianPROCQA%'` and matching
  nothing. A single term like `"Meridian"` has no special characters to
  strip, so it worked by accident - exactly the reported symptom. Fixing the
  escaping alone wouldn't have been enough, since SQL `LIKE` cannot express
  alternation at all: `{regex}` filters now use each engine's real boolean
  regex-match capability instead - PostgreSQL's `~` operator, DuckDB's
  `regexp_matches(col, pattern)` (DuckDB's own `~` operator silently
  misbehaves for strings, so it can't be shared across both engines). Which
  engine a query will use is now determined up front via a new
  `_get_active_sql_engine()` helper, since the WHERE-clause text is built
  once and can run on either engine depending on `sql_query()`'s routing.
  Verified end-to-end against DuckDB with the exact reported scenario; the
  investigation also ruled out the requirements doc's original suspect
  (`_apply_filters()`'s `pandas.Series.str.match()`), confirming it is
  unreachable dead code in the current SDK.

---

## [v3.0.7] - 2026-08-17

### Added
- `MediaPlanNotFoundError`, distinct from generic `StorageError`
  `MediaPlan.load()`'s only failure mode for a missing plan ID used to be a
  generic `StorageError` built from the full resolved local path (leaking the
  server's absolute filesystem layout) and indistinguishable by type from
  permission errors, corrupted reads, or S3 access failures. `read_mediaplan()`
  now checks file existence up front and raises `MediaPlanNotFoundError` (a
  `StorageError` subclass) with just the relative path. Since it subclasses
  `StorageError`, every existing `except StorageError` catch continues to work
  unchanged.
- `meta_is_archived` in `WorkspaceManager.list_campaigns()`'s SQL output
  `list_mediaplans()` already selected `meta_is_archived` in both its `SELECT`
  and `GROUP BY` clauses; `list_campaigns()` never did, so `include_archived=True`
  correctly changed *which* campaigns came back but no returned row said
  whether that campaign *is* archived. Purely additive — no behavior change for
  callers ignoring the new field.
- Auto-generated `meta.id` on JSON import
  `excel/importer.py` already auto-generates `meta.id` (`mediaplan_{8-hex}`)
  when the Media Plan ID cell is blank; `import_from_json()` had no equivalent,
  so a JSON payload with a missing/null `id` failed Pydantic validation
  outright. `import_from_json()` now applies the same convention immediately
  before validation, at the import call site only — `from_dict()`/`load()`/
  `clone()`/migration are unaffected, since a missing `id` there indicates
  corruption of an already-saved plan rather than a new import.
- `ValidationError.errors()` passthrough
  `mediaplanpy.exceptions.ValidationError` now exposes a `.errors()` method
  returning pydantic's structured per-field error list (field, message, input)
  when available, instead of only a flattened string message.

### Fixed
- JSON-import validation failures no longer double-wrapped into `StorageError`
  `import_from_json()` caught its own `ValidationError` (already built from
  pydantic's message, dev URL included) and re-wrapped it a second time into
  `StorageError`, discarding pydantic's structured `.errors()` list and
  collapsing the distinction between "the input data is invalid" and "a real
  storage/IO problem occurred." Genuine data-validation failures now propagate
  as `ValidationError` with `.errors()` intact; the schema-version-mismatch
  case still maps to a friendly `StorageError` as before.
- SQL filter values quoted by column type instead of guessed from value shape
  `_build_sql_filter_conditions()` decided whether to quote a scalar filter
  value based on whether the Python value looked numeric, not the target
  column's actual SQL type — a filter like
  `{"campaign_workflow_status_id": "1"}` (a `varchar` column, string value
  that looks numeric) was emitted unquoted, which Postgres rejected with
  `operator does not exist: character varying = integer`. Exact-match and
  range filters now quote based on the column's declared type from the
  canonical schema (`storage/schema_columns.py`); columns outside that schema
  keep the previous guess-from-value-shape behavior.
- Postgres error misclassified as a workspace-isolation error
  `_sql_query_postgres`'s exception handler classified *any* database error
  mentioning `"workspace_id"` anywhere in its text as a workspace-isolation
  problem. Since `_add_workspace_filter()` injects a `workspace_id` predicate
  into every query, and Postgres embeds the full failing SQL in its error
  text, that substring was present in essentially every SQL error regardless
  of cause — so an unrelated type mismatch (see above) was mislabeled as a
  workspace isolation error. The classifier now inspects psycopg2's structured
  diagnostics (`diag.column_name` / `pgcode`) instead of substring-matching
  the full error text.

---

## [v3.0.6] - 2026-08-14

### Added
- `include_archived` parameter on `WorkspaceManager.list_mediaplans()`
  Previously, `list_mediaplans()` had no archived-filtering concept at all —
  it always returned every media plan, archived or not, with no native way
  to exclude them. The new `include_archived` parameter defaults to `True`
  (preserving current behavior byte-for-byte, unlike `list_campaigns()`'s
  `include_archived` default of `False`, which matches *its* pre-existing
  always-exclude behavior). Setting `include_archived=False` adds a
  `WHERE meta_is_archived = FALSE OR meta_is_archived IS NULL` clause,
  mirroring the NULL-safe pattern already used by `list_campaigns()` — plans
  that have never been explicitly archived or restored (`meta_is_archived`
  is `NULL`) are still included. Purely additive — existing callers are
  unaffected.

---

## [v3.0.5] - 2026-08-12

### Added
- `include_archived` parameter on `WorkspaceManager.list_campaigns()`
  Previously, `list_campaigns()` hardcoded the exclusion of archived campaigns
  (`meta_is_archived = FALSE OR meta_is_archived IS NULL`) with no way to
  override it. The new `include_archived` parameter (default `False`, preserving
  current behavior byte-for-byte) allows callers to opt in to seeing archived
  campaigns. Purely additive — existing callers are unaffected.
- `allow_current` parameter on `MediaPlan.archive()`
  Archiving a campaign has always been implemented client-side as a loop over
  the campaign's plans, but that loop could never complete: `archive()` always
  raised on the campaign's current plan, and every campaign has one. The new
  `allow_current` parameter (default `False`, preserving current behavior and
  error message byte-for-byte) lets callers explicitly archive a current plan
  as part of a campaign-level cascade. When used, `is_current` is preserved
  (not cleared), so `restore()` reinstates the plan as current with no
  re-election step. Intended for campaign-level cascade archival only — see
  the `archive()` docstring for the caveat on using it against a single plan
  of an otherwise-live campaign.
- Relaxed the `is_current`/`is_archived` mutual-exclusion invariant
  Removed the "cannot be both current and archived" checks in
  `Meta.validate_model()` and `SchemaValidator._validate_meta_v2_consistency()`.
  These flags answer different questions (which plan is authoritative vs.
  whether it's active) and are only contradictory for plan-level archival,
  which the default `archive()` guard above continues to prevent. No JSON
  Schema change — the constraint was SDK-side only.
- `MediaPlan.load(campaign_id=...)` now resolves archived campaigns
  Internally passes `include_archived=True` to `list_campaigns()` so that a
  campaign whose current plan has been archived (via `allow_current=True`)
  remains loadable by `campaign_id` — required for the campaign-archive-cascade
  UI flow to view/restore an archived campaign.

---

## [v3.0.4] - 2026-05-12

### Fixed
- Excel export of metric values on aggregate line items (`is_aggregate=True`)
  Aggregate rows store summary values directly rather than deriving them from
  a base metric and coefficient. The exporter previously applied the standard
  `=IF(cpu=0, 0, cost_total/cpu)` formula path to these rows, which evaluated
  to 0 when `cost_total=0` — masking the actual stored metric value (e.g.
  `metric_reach` on a campaign-level rollup). Aggregate rows now write metric
  values verbatim and leave coefficient columns blank.
- Excel export of custom metrics without a Dictionary entry
  When a custom metric (e.g. `metric_custom1`) had no entry in the plan's
  Dictionary, `metric_custom*_cpu` columns were created (defaulted to
  `cost_per_unit`) but never populated with a coefficient, so the metric's
  formula referenced an empty cell and evaluated to 0. The coefficient
  population logic now applies the same `cost_per_unit` default as column
  creation, so the values round-trip correctly.

---

## [v3.0.3] - 2026-03-08

### Added
- **`adbudg` formula type**: New diminishing-returns response curve formula for metrics.
  Formula: `metric_value = coefficient * base^parameter2 / (parameter1 + base^parameter2)`.
  Supports forward calculation, reverse coefficient solving, and full Excel round-trip
  (export/import) with coefficient, parameter1, and parameter2 columns.

---

## [v3.0.2] - 2026-03-03

### Fixed
- `MediaPlan.load(campaign_id=...)`
  Loading a media plan by `campaign_id` now correctly resolves the campaign's current media plan via `workspace.list_campaigns()` and loads it by its `meta_id`. Previously, `load()` incorrectly attempted to open a file named after the campaign ID, which does not exist. The deprecation warning has been removed as this is a valid and common use case.

### Added
- `examples/examples_04_load_mediaplan.py`
  New `load_by_campaign_id()` example demonstrating how to load a media plan using a campaign ID, including how the SDK resolves the campaign to its current media plan behind the scenes.

---

## [v3.0.1] - 2026-02-19

### Fixed
- `MediaPlan.save()`
  No longer resets `meta.created_at` when overwriting an existing media plan. The original creation timestamp is now preserved across saves; `created_at` is only set on the initial save.
- `SchemaMigrator`
  Migration from v2.0 to v3.0 now preserves the original `meta.created_at` value. Migration metadata (source version, target version, migration timestamp) is recorded in `meta.custom_properties.schema_migration`.
- `Workspace.list_campaigns()`
  Fixed invalid SQL generated when user-specified filters were applied. The `_add_sql_filters` helper now correctly appends conditions with `AND` when a `WHERE` clause already exists, rather than producing a duplicate `WHERE` keyword.

### Security
- `Workspace.sql_query()`
  Blocked SQL workspace isolation bypass via `UNION` operators, subqueries, and multi-statement queries. User-supplied SQL is now validated to prevent cross-workspace data access.

### Improved
- `examples/examples_08_list_objects.py`
  Updated to make proper use of the SDK list methods' built-in filter parameters (`list_mediaplans()`, `list_campaigns()`, `list_lineitems()`), replacing manual post-query filtering.

---

## [v3.0.0] - 2026-01-30

### Major Release - Schema v3.0 Support

This is a major release with comprehensive enhancements across schema support, formula systems, Excel integration, CLI capabilities, and developer documentation.

### Added
- **Schema v3.0 Support** (40+ more fields: 155 vs 116 in v2.0)
  - Target audiences and locations now support arrays with 13+ attributes each
  - Metric formulas for calculated metrics (power functions, conversion rates, cost-per-unit, constant)
  - Campaign KPI tracking fields (kpi_name1-5, kpi_value1-5)
  - Custom dimension fields at Meta and Campaign levels (dim_custom1-5)
  - Custom properties objects for extensibility at all levels
  - 11 new standard metrics (view_starts, view_completions, reach, units, impression_share, page_views, likes, shares, comments, conversions)
  - Buy information fields (buy_type, buy_commitment)
  - Multi-currency support (cost_currency_exchange_rate)
  - Budget constraints for optimization (cost_minimum, cost_maximum)
  - Aggregation support (is_aggregate, aggregation_level)

- **3-Tier Formula Hierarchy System**
  - LineItem-level formula overrides for flexible metric calculations
  - Dictionary-level default formulas for workspace-wide consistency
  - System-level defaults for standard behavior
  - New `LineItem.get_metric_formula_definition()` method for hierarchy resolution
  - Enhanced `LineItem.configure_metric_formula()` with formula_type and base_metric override support
  - Support for all formula types: cost_per_unit, conversion_rate, power_function, constant
  - Automatic dependency resolution and topological sorting for formula calculations
  - Formula recalculation engine with support for complex dependency chains

- **Enhanced CLI for Workspace Management**
  - New `mediaplanpy workspace upgrade` command for v2.0 → v3.0 migration
  - Interactive upgrade process with automatic backup creation
  - Workspace validation and version enforcement
  - Improved command structure and help documentation
  - Better error handling and user feedback

- **Revamped Examples Library**
  - Comprehensive examples demonstrating all key SDK functionality
  - Formula system examples (hierarchy, calculation, dependency chains)
  - Excel import/export workflows with formula preservation
  - Database integration patterns
  - Advanced querying and analytics examples
  - Migration and workspace management examples
  - All examples updated for v3.0 schema

### Improved
- **Migration System** (CLI-based)
  - **Use CLI command `mediaplanpy workspace upgrade` for migration** (recommended approach)
  - v2.0 → v3.0 migration with automatic audience/location name generation
  - Systematic name generation rules for target_audiences and target_locations arrays
  - Dictionary field renamed: custom_dimensions → lineitem_custom_dimensions
  - Workspace upgrade requires explicit user action (strict version enforcement)
  - Automatic validation before and after migration
  - Comprehensive backup system before any destructive operations
  - Removed v0.0 and v1.0 support (breaking change)

- **Excel Integration - Formula-Aware Import/Export**
  - **Export**: Smart column generation based on dictionary formula configurations
    - Creates appropriate columns (CPU, CVR, Constant, Coefficient) based on formula_type
    - Excel formulas match actual formula types (not hardcoded to cost_per_unit)
    - Coefficient values exported from metric_formulas when available
    - Reverse-calculated coefficients when formulas don't exist
    - Parameter columns for power_function formulas
    - Separate Target Audiences and Target Locations worksheets
  - **Import**: Automatic coefficient updates from edited values
    - Reads coefficient/parameter columns based on dictionary configuration
    - Updates metric_formulas coefficients when users edit metric values
    - Processes dependencies in topological order (handles chains)
    - Formula-aware: respects formula_type when calculating coefficients
    - Preserves lineitem-level formula overrides through JSON column
  - Full round-trip integrity: export → edit → import → export maintains all formula configurations

- **Database & Storage**
  - Enhanced database schema migration with ALTER TABLE support for v2.0 → v3.0 upgrades
  - New columns for target_audiences, target_locations, metric_formulas (JSONB)
  - Automatic backups created before workspace upgrades
  - Comprehensive validation for new array and formula structures
  - Improved PostgreSQL performance with optimized indexing

- **Workspace Management**
  - Strict version enforcement: v3.0 SDK only loads v3.0 workspaces
  - Enhanced workspace settings validation
  - Improved error messages for version mismatches
  - Better logging and diagnostic information

### Breaking Changes
- **SDK v3.0.x only loads v3.0 workspaces**
  - v2.0 workspaces must be explicitly upgraded using `mediaplanpy workspace upgrade`
  - SDK v2.0.7 must be used to continue working with v2.0 workspaces
  - No backward compatibility - strict version enforcement
- **Schema v0.0 and v1.0 no longer supported** (removed from codebase)
- **Campaign schema restructuring** (handled automatically by migration):
  - Audience fields (audience_name, audience_age_*, audience_gender, audience_interests) → target_audiences array
  - Location fields (location_type, locations) → target_locations array
- **Dictionary schema changes**:
  - custom_dimensions renamed to lineitem_custom_dimensions
  - New groups added: meta_custom_dimensions, campaign_custom_dimensions, standard_metrics
- **Excel format changes**:
  - Separate worksheets for Target Audiences and Target Locations
  - Formula-specific columns (CPU/CVR/Constant/Coefficient) based on dictionary configuration
  - Metric Formulas JSON column for lineitem-level overrides
- **API changes**:
  - Removed deprecated from_v0_* and from_v1_* conversion methods
  - 47 methods updated to support new v3.0 schema structures

### Migration Guide
**For v2.0 Users**: To upgrade existing v2.0 workspaces to v3.0:
```bash
# Upgrade using CLI (recommended)
mediaplanpy workspace upgrade

# Or continue using SDK v2.0.7
pip install mediaplanpy==2.0.7
```

See detailed migration guide: [docs/MIGRATION_V2_TO_V3.md](docs/MIGRATION_V2_TO_V3.md)

### Documentation
- Updated README.md with v3.0 installation instructions and version guidance
- Updated GET_STARTED.md with v3.0 examples and migration paths
- New cloud_storage_configuration.md guide for S3 setup with workspace isolation best practices
- New database_configuration.md guide for PostgreSQL setup
- Revamped SDK_REFERENCE.md with v3.0 API documentation
- Complete examples library demonstrating all v3.0 features
- Migration guide with systematic rules for v2.0 → v3.0 transformation

### Technical Improvements
- Enhanced schema validation with comprehensive v3.0 field validation
- Improved error messages and logging throughout the SDK
- Better performance for formula calculations with optimized dependency resolution
- Memory optimization for large media plans with formulas
- Type hints and documentation improvements across codebase
- Enhanced test coverage for v3.0 features

### Version Compatibility
- **Python**: 3.8, 3.9, 3.10, 3.11, 3.12
- **Schema**: v3.0 (v2.0 migration support via CLI)
- **PyPI Package**: Available as `pip install mediaplanpy`

---

## [v2.0.7] - 2025-10-18

### Fixed
- `Workspace.list_campaigns()`
  Bug fix whereby duplicate entries were being returned in campaign list.


## [v2.0.6] - 2025-10-10

### Fixed
- `MediaPlan.load()`
  Change approach to loading S3 Storage Backend due to circular import issues on Linux.

### Improved
- `Workspace.create()`
  Optimized indexing for PostgreSQL database table and removed unnecessary indexes.
  Note: Existing databases are not automatically upgraded with new indexes.
- `Mediaplan.load()`, `Mediaplan.import_from_excel()`, `Mediaplan.import_from_json()`  
  Removed unnecessary media plan data validation for agency, advertiser, product and workflow_status id / names.


## [v2.0.5] - 2025-09-10

### Improved
- `MediaPlan.set_as_current()`
  Performance optimization for faster execution in large workspaces with cloud-based storage.
- `Workspace.sql_query()`  
  Performance optimization for single plan SQL queries on database enabled workspaces.


## [v2.0.4] - 2025-09-08

### Improved
- `Workspace.sql_query()`  
  Upgraded performance for S3 storage by querying Database (PostgreSQL) instead of Parquet files, when enabled.
- `Workspace.list_campaigns()`  
  Upgraded performance by leveraging native workspace.sql_query() method. 
- `Workspace.list_mediaplans()`  
  Upgraded performance by leveraging native workspace.sql_query() method. 
- `Workspace.list_lineitems()`  
  Upgraded performance by leveraging native workspace.sql_query() method. 


## [v2.0.3] - 2025-08-26

### Added
- S3 Storage Support  
  Cloud storage in S3 now supported across all core SDK functionality. Configure in Workspace Settings JSON. 


## [v2.0.2] - 2025-08-25

### Improved
- `MediaPlan.export_to_excel()`
  Added formulas for cost allocation and metric columns so that they auto-calculate with budget changes.
- `Workspace.create()`
  Upgraded to include database connection settings in default Workspace Settings for ease of configuration.


## [v2.0.1] - 2025-07-31

### Added
- `MediaPlan.archive(workspace_manager)`  
  Archive a media plan by marking it as archived (`is_archived=True`), saving its status and updating storage/database accordingly. 
  Prevents archiving if the plan is currently current (`is_current=True`).
- `MediaPlan.restore(workspace_manager)`  
  Restore an archived media plan by setting `is_archived=False` and updating storage/database accordingly.
- `MediaPlan.set_as_current(workspace_manager)`  
  Promotes the selected media plan to be the current version for its campaign, automatically demoting any other plans marked as current.
- `MediaPlan.save(set_as_current=True)` *(optional argument)*  
  New boolean flag added to the `save()` method to allow setting a plan as current at the time of saving.

### Improved
- `MediaPlan.export_to_excel()`  
  Enhanced layout and formatting of the exported Excel workbook, especially the **Dictionary** and **Documentation** worksheets, for improved readability and compliance with schema documentation standards.

### Fixed
- `MediaPlan.import()`  
  Improved validation to prevent duplicate line item IDs and custom column captions during plan import, ensuring better data integrity.