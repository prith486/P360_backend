import time
from typing import Any, Optional

# Simple in-memory TTL cache
_cache: dict = {}

def get_cached(key: str) -> Optional[Any]:
    if key in _cache:
        value, expires_at = _cache[key]
        if time.time() < expires_at:
            return value
        del _cache[key]
    return None

def set_cached(key: str, value: Any, ttl_seconds: int = 60):
    _cache[key] = (value, time.time() + ttl_seconds)

def invalidate_cache(prefix: str):
    keys_to_delete = [k for k in _cache if k.startswith(prefix)]
    for k in keys_to_delete:
        del _cache[k]
