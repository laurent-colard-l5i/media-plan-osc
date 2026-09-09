"""
Storage module for mediaplanpy.

This module provides functionality for reading and writing media plans
to various storage backends in different formats.
"""

import json
import logging
import threading
from collections import OrderedDict
from typing import Dict, Any, Optional, Tuple, Type, Union

from mediaplanpy.exceptions import StorageError, MediaPlanNotFoundError
from mediaplanpy.storage.base import StorageBackend
from mediaplanpy.storage.local import LocalStorageBackend
from mediaplanpy.storage.formats import (
    FormatHandler,
    get_format_handler_instance,
    JsonFormatHandler
)

logger = logging.getLogger("mediaplanpy.storage")

# Registry of storage backend classes with defensive S3 loading
_storage_backends = {
    'local': LocalStorageBackend,
}

# Try to register S3 backend - handles circular import issues
try:
    from mediaplanpy.storage.s3 import S3StorageBackend
    _storage_backends['s3'] = S3StorageBackend
    logger.debug("S3 storage backend registered successfully")
except ImportError as e:
    logger.warning(f"S3 storage backend not available: {e}")
except Exception as e:
    logger.error(f"Failed to register S3 storage backend: {e}")


# ── Backend instance cache ───────────────────────────────────────────────────
#
# get_storage_backend() is called many times per logical operation (every
# settings read/write, every DataSource/DataFile reload in downstream
# packages) and previously constructed a brand-new backend every single
# call. For LocalStorageBackend that's free (just path resolution), but
# S3StorageBackend.__init__() builds a boto3 client AND performs a live
# head_bucket() connectivity check - a real network round-trip - every time.
# That made repeated calls within one process pay for the same connectivity
# check over and over.
#
# The cache below reuses backend instances across calls that resolve to the
# same effective storage configuration, keyed by content (not by
# workspace_config's object identity, since every known caller constructs a
# fresh WorkspaceManager and a fresh resolved-config dict per call - an
# identity-based cache would never hit in practice).
_backend_cache: "OrderedDict[Tuple[str, str, str], StorageBackend]" = OrderedDict()
_backend_cache_lock = threading.Lock()

# Bounded + LRU so a long-running, multi-tenant process (e.g. an API server
# looping over many different workspaces) can't grow this cache forever.
_BACKEND_CACHE_MAXSIZE = 64


def _backend_cache_key(workspace_config: Dict[str, Any], mode: str) -> Tuple[str, str, str]:
    """
    Build a hashable cache key from the parts of workspace_config that
    determine a backend's identity/behavior.

    Includes workspace_id in addition to the mode-specific storage config:
    S3StorageBackend defaults its `prefix` to workspace_id when
    storage.s3.prefix is not set, so two workspaces with identical
    storage.s3 blocks but different ids can still resolve to different,
    non-interchangeable backends.
    """
    workspace_id = str(workspace_config.get('workspace_id', ''))
    storage_config = workspace_config.get('storage', {})
    mode_config = storage_config.get(mode, {})
    # sort_keys makes the key independent of dict insertion order; default=str
    # tolerates any non-JSON-native values rather than raising on them.
    mode_config_key = json.dumps(mode_config, sort_keys=True, default=str)
    return (workspace_id, mode, mode_config_key)


def clear_storage_backend_cache() -> None:
    """
    Clear all cached storage backend instances.

    get_storage_backend() normally reuses a backend instance across calls
    that resolve to the same effective storage configuration (see module
    docstring above). Call this to force fresh backends on the next call -
    for example after rotating credentials that a cached backend has no way
    to notice on its own (a boto3 client built from static
    AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY env vars does not re-read them
    after construction; one built from a profile or an IAM role's temporary
    credentials refreshes itself automatically and does not need this).
    """
    with _backend_cache_lock:
        _backend_cache.clear()


def get_storage_backend(workspace_config: Dict[str, Any]) -> StorageBackend:
    """
    Get a storage backend instance based on workspace configuration.

    Instances are cached and reused across calls whose effective storage
    configuration is identical (see clear_storage_backend_cache() to force
    a fresh instance). A cache hit skips backend construction entirely, so
    a backend that performs its own connectivity check in __init__ (as
    S3StorageBackend does) only pays that cost once per distinct
    configuration rather than on every call.

    Args:
        workspace_config: The resolved workspace configuration dictionary.

    Returns:
        A storage backend instance.

    Raises:
        StorageError: If no storage backend is available for the configured
            mode, or if backend construction fails. A failed construction is
            never cached, so the next call retries it from scratch.
    """
    storage_config = workspace_config.get('storage', {})
    mode = storage_config.get('mode')

    if not mode:
        raise StorageError("No storage mode specified in workspace configuration")

    if mode not in _storage_backends:
        available_modes = ', '.join(_storage_backends.keys())
        raise StorageError(
            f"No storage backend available for mode '{mode}'. "
            f"Available modes: {available_modes}"
        )

    cache_key = _backend_cache_key(workspace_config, mode)

    with _backend_cache_lock:
        cached = _backend_cache.get(cache_key)
        if cached is not None:
            _backend_cache.move_to_end(cache_key)
            return cached

    # Deliberately construct outside the lock: S3StorageBackend.__init__()
    # does network I/O (head_bucket), and holding the lock across that would
    # serialize backend construction for every workspace in the process, not
    # just the one currently being constructed. Two threads racing to build
    # the same not-yet-cached backend is harmless - both are valid instances
    # for the same config, and only one ends up cached below.
    backend_class = _storage_backends[mode]
    try:
        backend = backend_class(workspace_config)
    except Exception as e:
        raise StorageError(f"Failed to initialize {mode} storage backend: {e}")

    with _backend_cache_lock:
        _backend_cache[cache_key] = backend
        _backend_cache.move_to_end(cache_key)
        while len(_backend_cache) > _BACKEND_CACHE_MAXSIZE:
            _backend_cache.popitem(last=False)

    return backend


def read_mediaplan(workspace_config: Dict[str, Any], path: str, format_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Read a media plan from storage.

    Args:
        workspace_config: The resolved workspace configuration dictionary.
        path: The path to the media plan file.
        format_name: Optional format name to use. If not specified, inferred from path.

    Returns:
        The media plan data as a dictionary.

    Raises:
        MediaPlanNotFoundError: If no file exists at the given path.
        StorageError: If the media plan cannot be read.
    """
    # Get storage backend
    backend = get_storage_backend(workspace_config)

    # Check existence up front so a genuinely missing plan is distinguishable
    # from other storage failures (permission, corruption, network).
    if not backend.exists(path):
        raise MediaPlanNotFoundError(f"Media plan not found: {path}")

    # Get format handler
    if format_name:
        format_handler = get_format_handler_instance(format_name)
    else:
        format_handler = get_format_handler_instance(path)

    try:
        # Read file content
        with backend.open_file(path, 'r') as f:
            return format_handler.deserialize_from_file(f)
    except Exception as e:
        raise StorageError(f"Failed to read media plan from {path}: {e}")


def write_mediaplan(workspace_config: Dict[str, Any], data: Dict[str, Any], path: str,
                    format_name: Optional[str] = None, **format_options) -> None:
    """
    Write a media plan to storage.
    """
    # Get storage backend
    backend = get_storage_backend(workspace_config)

    # Get format handler
    if format_name:
        format_handler = get_format_handler_instance(format_name, **format_options)
    else:
        format_handler = get_format_handler_instance(path, **format_options)

    try:
        # Check if format requires binary mode
        mode = 'wb' if getattr(format_handler, 'is_binary', False) else 'w'

        # Write file content
        with backend.open_file(path, mode) as f:
            format_handler.serialize_to_file(data, f)
    except Exception as e:
        raise StorageError(f"Failed to write media plan to {path}: {e}")


# Build __all__ list dynamically based on available backends
__all__ = [
    'StorageBackend',
    'LocalStorageBackend',
    'FormatHandler',
    'JsonFormatHandler',
    'get_storage_backend',
    'clear_storage_backend_cache',
    'get_format_handler_instance',
    'read_mediaplan',
    'write_mediaplan'
]

# Add S3StorageBackend to exports if it was successfully imported
if 's3' in _storage_backends:
    __all__.append('S3StorageBackend')