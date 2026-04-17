"""
Delta compression for ARENA MQTT messages.

Computes the minimal diff between two JSON-serialized data dicts,
returning only changed fields. Used on the outbound publish path
to reduce MQTT payload sizes.
"""


def deep_diff(prev, next_val):
    """Compute the minimal delta between two data dicts.

    Both inputs must be JSON-primitive dicts (str, int, float, bool,
    None, dict, list — no custom objects). This is guaranteed when
    called after Object.json() serialization.

    Rules:
        - Recurse into nested dicts; identical sub-dicts are omitted.
        - None is a semantic delete and always flows through.
          None → None is a no-op (omitted).
        - Arrays compared by value (Python == does deep equality).
        - Keys in next_val but not prev are new → included.
        - Keys in prev but not next_val are removed → emitted as None.

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

        # Recurse into nested dicts
        if isinstance(pv, dict) and isinstance(nv, dict):
            sub = deep_diff(pv, nv)
            if sub:  # Only include if something changed
                diff[key] = sub
            continue

        # Primitives / lists: Python == handles deep equality
        if pv != nv:
            diff[key] = nv

    # Keys in prev but not next_val → semantic delete
    for key in prev:
        if key not in next_val:
            diff[key] = None

    return diff
