"""Tests for smart_cache — LRU cache with TTL support."""

import time
from solution import smart_cache


def test_basic_caching():
    """Cached function returns same result for same args without re-executing."""
    call_count = 0

    @smart_cache(maxsize=10, ttl=5.0)
    def add(a, b):
        nonlocal call_count
        call_count += 1
        return a + b

    assert add(1, 2) == 3
    assert add(1, 2) == 3
    assert call_count == 1  # second call was cached


def test_different_args_cached_separately():
    """Different arguments produce separate cache entries."""
    call_count = 0

    @smart_cache(maxsize=10, ttl=5.0)
    def multiply(a, b):
        nonlocal call_count
        call_count += 1
        return a * b

    assert multiply(2, 3) == 6
    assert multiply(3, 4) == 12
    assert multiply(2, 3) == 6
    assert call_count == 2


def test_lru_eviction():
    """When maxsize is exceeded, the least recently used entry is evicted."""
    @smart_cache(maxsize=2, ttl=5.0)
    def square(x):
        return x * x

    square(1)  # cache: {1}
    square(2)  # cache: {1, 2}
    square(3)  # cache: {2, 3} — 1 evicted

    info = square.cache_info()
    assert info["size"] <= 2

    # Calling square(1) again should be a miss (it was evicted)
    call_count_before = info["misses"]
    square(1)
    info_after = square.cache_info()
    assert info_after["misses"] == call_count_before + 1


def test_lru_access_order():
    """Accessing an entry makes it recently used, protecting it from eviction."""
    @smart_cache(maxsize=2, ttl=5.0)
    def identity(x):
        return x

    identity(1)  # cache: {1}
    identity(2)  # cache: {1, 2}
    identity(1)  # access 1, making 2 the LRU — cache: {2, 1}
    identity(3)  # evict 2 — cache: {1, 3}

    # 1 should still be cached (hit), 2 should be evicted (miss)
    info_before = identity.cache_info()
    identity(1)
    info_after = identity.cache_info()
    assert info_after["hits"] == info_before["hits"] + 1

    info_before2 = identity.cache_info()
    identity(2)
    info_after2 = identity.cache_info()
    assert info_after2["misses"] == info_before2["misses"] + 1


def test_ttl_expiration():
    """Entries expire after TTL seconds."""
    @smart_cache(maxsize=10, ttl=0.05)
    def greet(name):
        return f"hello {name}"

    greet("world")
    info1 = greet.cache_info()
    assert info1["misses"] == 1

    time.sleep(0.1)  # wait for TTL to expire

    greet("world")
    info2 = greet.cache_info()
    assert info2["misses"] == 2  # should be a miss after expiry


def test_cache_info():
    """cache_info() returns correct hits, misses, and size."""
    @smart_cache(maxsize=10, ttl=5.0)
    def inc(x):
        return x + 1

    inc(1)  # miss
    inc(2)  # miss
    inc(1)  # hit
    inc(3)  # miss
    inc(2)  # hit

    info = inc.cache_info()
    assert info["hits"] == 2
    assert info["misses"] == 3
    assert info["size"] == 3


def test_cache_clear():
    """cache_clear() resets the entire cache and counters."""
    @smart_cache(maxsize=10, ttl=5.0)
    def double(x):
        return x * 2

    double(5)
    double(5)
    assert double.cache_info()["hits"] == 1

    double.cache_clear()
    info = double.cache_info()
    assert info["hits"] == 0
    assert info["misses"] == 0
    assert info["size"] == 0

    # After clear, calling again should be a miss
    double(5)
    assert double.cache_info()["misses"] == 1


def test_efficiency_cached_calls():
    """Efficiency: 1000 cached calls to a slow function must complete in < 0.1s."""
    @smart_cache(maxsize=10, ttl=5.0)
    def slow_func(x):
        # Simulate slow work — only runs on cache miss
        time.sleep(0.01)
        return x

    # Prime the cache
    slow_func(42)

    start = time.perf_counter()
    for _ in range(1000):
        slow_func(42)
    elapsed = time.perf_counter() - start

    assert elapsed < 0.1, f"1000 cached calls took {elapsed:.3f}s (should be < 0.1s)"


def test_efficiency_many_keys():
    """Efficiency: 10000 distinct keys with maxsize=100 must complete in < 1s.

    This tests that eviction is O(1) amortized, not O(n) per eviction.
    """
    @smart_cache(maxsize=100, ttl=5.0)
    def compute(x):
        return x * 2

    start = time.perf_counter()
    for i in range(10000):
        compute(i)
    elapsed = time.perf_counter() - start

    assert elapsed < 1.0, f"10000 calls with eviction took {elapsed:.3f}s (should be < 1.0s)"
