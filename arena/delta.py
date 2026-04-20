"""
Delta compression for ARENA MQTT messages.

Computes the minimal diff between two JSON-serialized data dicts,
returning only changed top-level fields. Used on the outbound publish path
to reduce MQTT payload sizes.
"""


def shallow_diff(prev, next_val):
    """Compute the delta between two data dicts (top-level keys only).

    Compares top-level keys by value without recursing into nested objects.
    This ensures that complex nested structures (position, rotation, material, etc.)
    are always sent completely when they change, avoiding partial update issues.

    Args:
        prev: Previously published data dict.
        next_val: Current data dict to publish.

    Returns:
        Dict containing only changed fields. Empty {} means no changes.
    """
    diff = {}

    # Keys present in next_val: check for changes or additions
    for key, nv in next_val.items():
        if key not in prev:
            # New field
            diff[key] = nv
            continue

        pv = prev[key]

        # Both None → no-op (already deleted)
        if pv is None and nv is None:
            continue

        # Compare by value (no recursion into nested dicts/lists)
        if pv != nv:
            diff[key] = nv

    # Keys in prev but not next_val → semantic delete
    for key in prev:
        if key not in next_val:
            diff[key] = None

    return diff
