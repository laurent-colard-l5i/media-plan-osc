"""
Unit tests for the get_storage_backend() instance cache added in v3.0.12.

These tests use a fake backend class registered under a synthetic 'fake'
storage mode rather than LocalStorageBackend or S3StorageBackend, so they
exercise only the caching logic in mediaplanpy.storage - no filesystem or
network access, no boto3/moto dependency.
"""

import threading

import pytest

from mediaplanpy import storage as storage_module
from mediaplanpy.exceptions import StorageError
from mediaplanpy.storage import (
    clear_storage_backend_cache,
    get_storage_backend,
)
from mediaplanpy.storage.base import StorageBackend


class FakeBackend(StorageBackend):
    """Minimal concrete StorageBackend that records construction calls."""

    instances_created = 0
    fail_next = False

    def __init__(self, workspace_config):
        if FakeBackend.fail_next:
            FakeBackend.fail_next = False
            raise RuntimeError("simulated construction failure")
        FakeBackend.instances_created += 1
        super().__init__(workspace_config)

    # Abstract methods - unused by these tests, implemented to allow
    # instantiation.
    def exists(self, path):
        return False

    def read_file(self, path, binary=False):
        raise NotImplementedError

    def write_file(self, path, content):
        raise NotImplementedError

    def list_files(self, path, pattern=None):
        return []

    def delete_file(self, path):
        raise NotImplementedError

    def get_file_info(self, path):
        return {}

    def open_file(self, path, mode='r'):
        raise NotImplementedError


@pytest.fixture(autouse=True)
def fake_backend_registered(monkeypatch):
    """Register FakeBackend under mode 'fake' and reset its call counter."""
    monkeypatch.setitem(storage_module._storage_backends, 'fake', FakeBackend)
    FakeBackend.instances_created = 0
    FakeBackend.fail_next = False
    clear_storage_backend_cache()
    yield
    clear_storage_backend_cache()


def _config(bucket="bucket-a", workspace_id="workspace_1", **overrides):
    cfg = {
        "workspace_id": workspace_id,
        "storage": {
            "mode": "fake",
            "fake": {"bucket": bucket, "region": "us-east-2"},
        },
    }
    cfg["storage"]["fake"].update(overrides)
    return cfg


def test_same_effective_config_reuses_cached_instance():
    # Two independently-built dicts with identical content, exactly how
    # every real caller works today (fresh WorkspaceManager + fresh
    # resolved config per call) - must still hit the cache.
    backend1 = get_storage_backend(_config())
    backend2 = get_storage_backend(_config())

    assert backend1 is backend2
    assert FakeBackend.instances_created == 1


def test_different_bucket_gets_distinct_instance():
    backend1 = get_storage_backend(_config(bucket="bucket-a"))
    backend2 = get_storage_backend(_config(bucket="bucket-b"))

    assert backend1 is not backend2
    assert FakeBackend.instances_created == 2


def test_different_workspace_id_gets_distinct_instance_even_if_storage_config_matches():
    # Same bucket/region config for two different workspaces (e.g. both
    # omitting an explicit prefix, which S3StorageBackend defaults to
    # workspace_id) must never share a backend.
    backend1 = get_storage_backend(_config(workspace_id="workspace_1"))
    backend2 = get_storage_backend(_config(workspace_id="workspace_2"))

    assert backend1 is not backend2
    assert FakeBackend.instances_created == 2


def test_key_order_independence():
    """Dict key insertion order must not affect cache hits."""
    cfg1 = _config()
    cfg2 = {
        "storage": {"fake": dict(reversed(list(cfg1["storage"]["fake"].items()))), "mode": "fake"},
        "workspace_id": cfg1["workspace_id"],
    }

    backend1 = get_storage_backend(cfg1)
    backend2 = get_storage_backend(cfg2)

    assert backend1 is backend2
    assert FakeBackend.instances_created == 1


def test_failed_construction_is_not_cached_and_is_wrapped_as_storage_error():
    FakeBackend.fail_next = True

    with pytest.raises(StorageError):
        get_storage_backend(_config(bucket="bucket-c"))

    # Retrying with the same config must attempt construction again, not
    # return a poisoned/empty cache entry.
    backend = get_storage_backend(_config(bucket="bucket-c"))
    assert backend is not None
    assert FakeBackend.instances_created == 1


def test_unknown_mode_raises_without_touching_cache():
    with pytest.raises(StorageError):
        get_storage_backend({"storage": {"mode": "nonexistent"}})

    assert len(storage_module._backend_cache) == 0


def test_clear_storage_backend_cache_forces_reconstruction():
    get_storage_backend(_config())
    assert FakeBackend.instances_created == 1

    clear_storage_backend_cache()

    get_storage_backend(_config())
    assert FakeBackend.instances_created == 2


def test_cache_is_bounded_and_evicts_least_recently_used(monkeypatch):
    monkeypatch.setattr(storage_module, "_BACKEND_CACHE_MAXSIZE", 2)

    a = get_storage_backend(_config(bucket="a"))
    b = get_storage_backend(_config(bucket="b"))
    # Touch 'a' again so 'b' becomes the least-recently-used entry.
    get_storage_backend(_config(bucket="a"))
    c = get_storage_backend(_config(bucket="c"))  # should evict 'b', not 'a'

    assert FakeBackend.instances_created == 3

    # 'a' should still be cached (was touched most recently before 'c').
    a_again = get_storage_backend(_config(bucket="a"))
    assert a_again is a
    assert FakeBackend.instances_created == 3

    # 'b' should have been evicted and require reconstruction.
    b_again = get_storage_backend(_config(bucket="b"))
    assert b_again is not b
    assert FakeBackend.instances_created == 4


def test_concurrent_calls_for_same_config_converge_to_one_cached_instance():
    results = []

    def worker():
        results.append(get_storage_backend(_config(bucket="concurrent")))

    threads = [threading.Thread(target=worker) for _ in range(16)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(results) == 16
    # A race constructing duplicates before the first is cached is
    # tolerated (see comment in get_storage_backend()), but the cache must
    # converge on a single instance for subsequent callers.
    final = get_storage_backend(_config(bucket="concurrent"))
    assert all(r.config == final.config for r in results)
    assert get_storage_backend(_config(bucket="concurrent")) is final
