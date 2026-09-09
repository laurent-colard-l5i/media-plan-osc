"""
Media Plan OSC - Python SDK for Media Plans.

A lightweight, open-source Python SDK for interacting with the open data
standard for media plans.
"""

# Central Version Definitions - Updated for v3.0
__version__ = '3.0.12'          # SDK version
__schema_version__ = '3.0'     # Current schema version supported

VERSION_NOTES = {
    '1.0.0': 'v1.0 schema support with new versioning strategy - Schema 1.0',
    '2.0.0': 'v2.0 schema support with v1.0 backwards compatibility - v0.0 support removed',
    '2.0.1': 'v2.0 schema support with minor non-breaking functionality upgrades',
    '2.0.2': 'v2.0 schema support with minor non-breaking functionality upgrades',
    '2.0.3': 'Implement support for S3 storage',
    '2.0.4': 'Performance upgrades for S3 storage',
    '2.0.5': 'Performance upgrades for S3 storage - continued',
    '2.0.6': 'Miscellaneous minor fixes / upgrades',
    '2.0.7': 'Bug fix in workspace.list_campaigns',
    '3.0.0': 'v3.0 schema support - Target audiences/locations arrays, metric formulas, 42+ new fields - v0.0 and v1.0 support removed',
    '3.0.1': 'Bug fixes: MediaPlan.save() created_at preservation, SQL filter generation, SQL injection prevention, examples update',
    '3.0.2': 'Fix MediaPlan.load(campaign_id=...) to resolve current media plan via workspace query',
    '3.0.3': 'Add adbudg (diminishing returns) formula type support',
    '3.0.4': 'Bug fixes: Excel export of metric values on aggregate line items and custom metrics without dictionary entries',
    '3.0.5': 'Add include_archived parameter to workspace.list_campaigns(); add allow_current override to MediaPlan.archive() to support campaign-level archive cascades (purely additive)',
    '3.0.6': 'Add include_archived parameter to workspace.list_mediaplans() (defaults to True, preserving existing behavior)',
    '3.0.7': 'MCP QA triage fixes: list_campaigns() now selects meta_is_archived; add MediaPlanNotFoundError distinct from StorageError; SQL filter values quoted by column type instead of guessed from value shape; JSON import auto-generates meta.id when missing; JSON-import validation failures propagate as ValidationError instead of being double-wrapped into StorageError',
    '3.0.8': 'MCP regression triage fixes: Meta.created_at now stamped with UTC instead of naive local time; {regex} filters use each engine\'s native regex matching (PostgreSQL ~, DuckDB regexp_matches()) instead of a SQL LIKE emulation that silently stripped alternation/anchors',
    '3.0.9': 'Fix Excel export crash introduced by 3.0.8\'s UTC-aware Meta.created_at - openpyxl rejects tz-aware datetimes, so the exporter now strips tzinfo for the cell and the importer reattaches UTC on the way back in',
    '3.0.10': 'Schema exposure for agent-authored media plans: new schema.get_schema()/get_schema_bundle()/get_example() serve the bundled definitions as self-contained documents with $refs resolved; JSON import now auto-generates campaign.id and line item ids as well as meta.id, matching MediaPlan.create() and the Excel importer',
    '3.0.11': 'Add campaign lifecycle methods to WorkspaceManager: archive_campaign(), restore_campaign(), delete_campaign(). Each cascades over the campaign\'s media plans, because campaigns are derived from plans and have no stored state of their own. Adds CampaignNotFoundError. Purely additive.',
    '3.0.12': 'Performance upgrade: get_storage_backend() now reuses backend instances across calls with the same effective storage configuration instead of constructing a new one every call. S3StorageBackend.__init__() performs a live head_bucket() connectivity check, so callers that invoke get_storage_backend() many times per logical operation (as several downstream packages do) were paying that network round-trip repeatedly for no reason. Cache is keyed by content (workspace_id + mode + mode-specific storage config), not by object identity, since callers typically pass a freshly-built config each time. New clear_storage_backend_cache() forces fresh instances (e.g. after external credential rotation). Purely additive/non-breaking.',
}

# Schema version compatibility constants - Updated for v3.0
CURRENT_MAJOR = 3
CURRENT_MINOR = 0
SUPPORTED_MAJOR_VERSIONS = [2, 3]  # v0.0 and v1.0 no longer supported - only v2.0 and v3.0

# Setup package-level logger
import logging

logger = logging.getLogger("mediaplanpy")
logger.setLevel(logging.INFO)

# Import workspace module
from mediaplanpy.workspace import (
    WorkspaceManager,
    WorkspaceError,
    WorkspaceNotFoundError,
    WorkspaceValidationError
)

# Import exceptions
from mediaplanpy.exceptions import (
    MediaPlanError,
    SchemaError,
    SchemaVersionError,
    SchemaRegistryError,
    SchemaMigrationError,
    ValidationError,
    StorageError,
    FileReadError,
    FileWriteError,
    S3Error,
    DatabaseError,
    WorkspaceInactiveError,
    FeatureDisabledError,
    CampaignNotFoundError
)

# Import schema module
from mediaplanpy.schema import (
    get_current_version,
    get_supported_versions,
    validate,
    validate_file,
    migrate,
    SchemaRegistry,
    SchemaValidator,
    SchemaMigrator,
    SchemaManager
)

# Import models
from mediaplanpy.models import (
    BaseModel,
    LineItem,
    Campaign,
    TargetAudience,
    TargetLocation,
    MetricFormula,
    Dictionary,
    CustomFieldConfig,
    MetricFormulaConfig,
    CustomMetricConfig,
    MediaPlan,
    Meta
)

# Import storage module
from mediaplanpy.storage import (
    read_mediaplan,
    write_mediaplan,
    get_storage_backend,
    clear_storage_backend_cache,
    get_format_handler_instance,
    JsonFormatHandler
)

# Import Excel module
from mediaplanpy.excel import (
    export_to_excel,
    import_from_excel,
    update_from_excel,
    validate_excel,
    ExcelFormatHandler
)

# Database integration now uses DatabaseMixin inheritance (no monkey patching needed)
# Check if database dependencies are available
try:
    import psycopg2
    _database_available = True
except ImportError:
    _database_available = False
    logger.debug("Database functionality not available - psycopg2-binary not installed")

__all__ = [
    # Version information
    '__version__',
    '__schema_version__',
    'VERSION_NOTES',
    'CURRENT_MAJOR',
    'CURRENT_MINOR',
    'SUPPORTED_MAJOR_VERSIONS',

    # Workspace
    'WorkspaceManager',
    'WorkspaceError',
    'WorkspaceNotFoundError',
    'WorkspaceValidationError',

    # Exceptions
    'MediaPlanError',
    'SchemaError',
    'SchemaVersionError',
    'SchemaRegistryError',
    'SchemaMigrationError',
    'ValidationError',
    'StorageError',
    'FileReadError',
    'FileWriteError',
    'S3Error',
    'DatabaseError',
    'WorkspaceInactiveError',
    'FeatureDisabledError',
    'CampaignNotFoundError',

    # Schema
    'get_current_version',
    'get_supported_versions',
    'validate',
    'validate_file',
    'migrate',
    'SchemaRegistry',
    'SchemaValidator',
    'SchemaMigrator',
    'SchemaManager',

    # Models
    'BaseModel',
    'LineItem',
    'Campaign',
    'TargetAudience',
    'TargetLocation',
    'MetricFormula',
    'Dictionary',
    'CustomFieldConfig',
    'MetricFormulaConfig',
    'CustomMetricConfig',
    'MediaPlan',
    'Meta',

    # Storage
    'read_mediaplan',
    'write_mediaplan',
    'get_storage_backend',
    'clear_storage_backend_cache',
    'get_format_handler_instance',
    'JsonFormatHandler',

    # Excel
    'export_to_excel',
    'import_from_excel',
    'update_from_excel',
    'validate_excel',
    'ExcelFormatHandler',
]

# Add database availability info
def is_database_available():
    """
    Check if database functionality is available.

    Returns:
        True if psycopg2-binary is installed and database functionality is available.
    """
    return _database_available

def get_version_info():
    """
    Get detailed version information.

    Returns:
        Dictionary containing SDK version, schema version, and release notes.
    """
    return {
        'sdk_version': __version__,
        'schema_version': __schema_version__,
        'release_notes': VERSION_NOTES.get(__version__, 'No release notes available'),
        'supported_major_versions': SUPPORTED_MAJOR_VERSIONS,
        'current_major': CURRENT_MAJOR,
        'current_minor': CURRENT_MINOR
    }