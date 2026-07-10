"""
Publish throttle: per-object-id rate limiting and duplicate-payload suppression.

Two independent checks are applied before each MQTT publish:

1. **Rate limiting** — if the same object_id has been published ≥10 times within
   the last second (i.e., the average inter-message interval falls below 100 ms),
   the message is dropped and a warning is printed.

2. **Duplicate suppression** — if the outgoing payload is identical to the previous
   payload for the same object_id (ignoring the top-level ``timestamp`` field), the
   message is dropped and a warning is printed because it carries no new scene-graph
   information.

Both checks are intentionally lightweight (O(k) where k ≤ RATE_LIMIT per object)
to minimise impact on local publish performance.
"""

import json
import time
from collections import deque

# Maximum allowed publishes per object_id within WINDOW_SECS (100 ms average interval)
RATE_LIMIT = 10
# Sliding-window width in seconds
WINDOW_SECS = 1.0


class PublishThrottle:
    """
    Tracks per-object-id publish rates and payload fingerprints.

    Instantiate once per :class:`~arena.scene.Scene` and call :meth:`check`
    before every ``transport.publish``.
    """

    def __init__(self):
        # object_id -> deque of float (unix timestamps of recent publishes)
        self._timestamps: dict[str, deque] = {}
        # object_id -> canonical payload string (sans timestamp) of last publish
        self._last_payload: dict[str, str] = {}

    def check(self, object_id: str, payload_str: str) -> tuple[bool, str | None]:
        """
        Decide whether a publish should proceed.

        Args:
            object_id: Identifier of the object being published.
            payload_str: Serialised JSON payload that would be sent to MQTT.

        Returns:
            ``(True, None)`` when the publish is allowed and the internal state
            has been updated to reflect it.
            ``(False, warning_message)`` when the publish should be suppressed;
            the caller should print / log the returned *warning_message*.
        """
        if not object_id:
            return True, None

        canonical = _canonical_payload(payload_str)

        # --- duplicate check ---
        if self._last_payload.get(object_id) == canonical:
            return False, (
                f"[WARNING] Suppressed duplicate publish for '{object_id}': "
                "payload unchanged (sans timestamp). No update sent."
            )

        # --- rate check ---
        now = time.time()
        q = self._timestamps.setdefault(object_id, deque())
        cutoff = now - WINDOW_SECS
        while q and q[0] < cutoff:
            q.popleft()
        if len(q) >= RATE_LIMIT:
            return False, (
                f"[WARNING] Publish rate exceeded for '{object_id}': "
                f">{RATE_LIMIT} messages/sec. No update sent."
            )

        # Record this publish
        q.append(now)
        self._last_payload[object_id] = canonical
        return True, None


def _canonical_payload(payload_str: str) -> str:
    """Return *payload_str* with the top-level ``timestamp`` field removed.

    Produces a stable, sorted JSON string used as a duplicate fingerprint.
    Falls back to the raw string if parsing fails.
    """
    try:
        d = json.loads(payload_str)
        d.pop("timestamp", None)
        return json.dumps(d, sort_keys=True)
    except (json.JSONDecodeError, TypeError, AttributeError):
        return payload_str
