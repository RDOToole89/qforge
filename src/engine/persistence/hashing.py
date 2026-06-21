"""Canonical hashing helpers for stable, reproducible identifiers.

Why this exists
---------------
We often want a short, stable fingerprint of a configuration or result so we can
use it in filenames, manifests, and deduplication. Python dict iteration order,
whitespace, or incidental types (e.g., numpy scalars) can change a naive JSON
dump, producing different hashes even when the *semantic* content is the same.

This module creates a canonical JSON representation and hashes that
representation. It is **not** for cryptographic security; SHA-1 is fine for
filenames and dedup keys but not for security. If you need a stronger hash,
use `blake2_of`.

Key functions
-------------
- canonical_dumps(data): Stable JSON string (sorted keys, no extra spaces).
- sha1_of(data): SHA-1 of canonical_dumps(data).
- short_hash(data, length=8): Truncated SHA-1 for compact IDs.
- blake2_of(data, digest_size=16): Stronger/faster general-purpose hash.
- hash_file(path, algo="sha1"): Hash a file in chunks (for large artifacts).

Notes:
-----
- Lists/tuples keep their order (as they should).
- Dicts are sorted by key.
- `exclude_none=True` removes keys whose value is `None` (useful for configs).
- Strings can be Unicode-normalized (default NFC) to avoid accidental
  differences from combining characters, etc.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import unicodedata
from collections.abc import Mapping
from pathlib import Path
from typing import Any, cast


def canonical_dumps(
    data: Mapping[str, Any],
    *,
    exclude_none: bool = True,
    sort_keys: bool = True,
    unicode_normalize: str | None = "NFC",
    float_precision: int | None = None,
) -> str:
    """Serialize a mapping to a stable JSON string.

    Parameters
    ----------
    data : Mapping[str, Any]
        The object to serialize (typically a dict-like config).
    exclude_none : bool
        If True, drop keys with value None during normalization.
    sort_keys : bool
        Sort dict keys for deterministic ordering.
    unicode_normalize : Optional[str]
        Apply Unicode normalization (e.g., "NFC") to all strings. Use None to disable.
    float_precision : Optional[int]
        If set, round floats to this many decimal places before dumping.

    Returns:
    -------
    str
        Stable JSON string with separators (',', ':') and ensure_ascii=False.
    """
    normalized = _normalize(
        data,
        exclude_none=exclude_none,
        unicode_normalize=unicode_normalize,
        float_precision=float_precision,
    )
    return json.dumps(
        normalized,
        sort_keys=sort_keys,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,  # last-resort fence
    )


def sha1_of(data: Mapping[str, Any]) -> str:
    """SHA-1 hash (hex) of the canonical JSON for `data` (backward compatible)."""
    s = canonical_dumps(data)
    return hashlib.sha1(s.encode("utf-8")).hexdigest()


def short_hash(data: Mapping[str, Any], length: int = 8) -> str:
    """Convenience: first `length` chars of sha1_of(data)."""
    return sha1_of(data)[: int(length)]


def blake2_of(
    data: Mapping[str, Any],
    *,
    digest_size: int = 16,
) -> str:
    """BLAKE2b hash (hex) of the canonical JSON for `data`.

    Use this if you want something faster/stronger than SHA-1 for IDs.
    """
    s = canonical_dumps(data)
    return hashlib.blake2b(s.encode("utf-8"), digest_size=digest_size).hexdigest()


def hash_file(path: str | Path, *, algo: str = "sha1", chunk_size: int = 8192) -> str:
    """Hash a file in chunks; returns hex digest.

    Parameters
    ----------
    path : str | Path
        File to hash.
    algo : str
        Any hashlib algorithm name (e.g., 'sha1', 'blake2b', 'md5' for testing).
    chunk_size : int
        Read size for streaming.

    Examples:
    --------
    >>> hash_file("results/foo.json", algo="blake2b")
    """
    h = hashlib.new(algo)
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


# -------- internals --------


def _normalize(
    obj: Any,
    *,
    exclude_none: bool,
    unicode_normalize: str | None,
    float_precision: int | None,
) -> Any:
    """Recursively convert `obj` into JSON-serializable, canonical form."""
    # Pydantic models
    if hasattr(obj, "model_dump"):
        try:
            obj = obj.model_dump(exclude_none=exclude_none)
        except TypeError:
            obj = obj.model_dump()

    # Dataclasses
    if dataclasses.is_dataclass(obj):
        obj = dataclasses.asdict(cast("Any", obj))

    # Path-like
    if isinstance(obj, Path):
        return str(obj)

    # Mapping
    if isinstance(obj, Mapping):
        out = {}
        for k, v in obj.items():
            if exclude_none and v is None:
                continue
            out[str(k)] = _normalize(
                v,
                exclude_none=exclude_none,
                unicode_normalize=unicode_normalize,
                float_precision=float_precision,
            )
        return out

    # Set -> sorted list (stable)
    if isinstance(obj, set):
        return [
            _normalize(
                x,
                exclude_none=exclude_none,
                unicode_normalize=unicode_normalize,
                float_precision=float_precision,
            )
            for x in sorted(obj, key=_sort_key)
        ]

    # Iterable (list/tuple)
    if isinstance(obj, (list, tuple)):
        return [
            _normalize(
                x,
                exclude_none=exclude_none,
                unicode_normalize=unicode_normalize,
                float_precision=float_precision,
            )
            for x in obj
        ]

    # Numpy scalars (without importing numpy): duck-typed via .item()
    if hasattr(obj, "item") and callable(obj.item):
        try:
            return obj.item()
        except Exception:
            pass

    # Floats with precision control
    if isinstance(obj, float) and float_precision is not None:
        return round(obj, int(float_precision))

    # Strings with Unicode normalization
    if isinstance(obj, str) and unicode_normalize:
        return unicodedata.normalize(cast("Any", unicode_normalize), obj)

    # Bytes -> hex
    if isinstance(obj, (bytes, bytearray, memoryview)):
        return bytes(obj).hex()

    # Everything else: must be JSON-encodable; fallback to str if not
    try:
        json.dumps(obj)
        return obj
    except TypeError:
        return str(obj)


def _sort_key(x: Any) -> str:
    """Stable sort key for sets: stringified, lower-cased."""
    return str(x).lower()
