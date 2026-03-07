import hashlib
from datetime import datetime, timedelta

# in-memory dict cache, key = MD5 hash, TTL = 24 hours
_cache = {}

def get_cached_response(prompt: str) -> dict | None:
    key = hashlib.md5(prompt.encode('utf-8')).hexdigest()
    if key in _cache:
        entry = _cache[key]
        if datetime.now() < entry["expires_at"]:
            return entry["data"]
        else:
            del _cache[key] # Expired
    return None

def set_cached_response(prompt: str, data: dict):
    key = hashlib.md5(prompt.encode('utf-8')).hexdigest()
    expires_at = datetime.now() + timedelta(hours=24)
    _cache[key] = {
        "data": data,
        "expires_at": expires_at
    }
