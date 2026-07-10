"""
Tests for PublishThrottle (arena/utils/publish_throttle.py).

Covers:
- Duplicate suppression (same payload sans timestamp)
- Rate limiting (>RATE_LIMIT messages/sec per object_id)
- Independence of checks across different object_ids
- Allow list after duplicate resets (payload changes)
- Allow list when rate window slides
"""

import json
import time
import unittest
from unittest.mock import patch

from arena.utils.publish_throttle import (
    RATE_LIMIT,
    WINDOW_SECS,
    PublishThrottle,
    _canonical_payload,
)


def _make_payload(object_id, action="update", color="#ff0000", timestamp="2024-01-01T00:00:00.000Z"):
    return json.dumps(
        {
            "object_id": object_id,
            "action": action,
            "type": "object",
            "timestamp": timestamp,
            "data": {"object_type": "box", "color": color},
        },
        sort_keys=True,
    )


class TestCanonicalPayload(unittest.TestCase):
    def test_strips_timestamp(self):
        payload = json.dumps({"object_id": "a", "action": "update", "timestamp": "2024-01-01T00:00:00Z"})
        canonical = _canonical_payload(payload)
        parsed = json.loads(canonical)
        self.assertNotIn("timestamp", parsed)
        self.assertEqual(parsed["object_id"], "a")

    def test_identical_payloads_different_timestamps(self):
        p1 = _make_payload("box1", timestamp="2024-01-01T00:00:00.000Z")
        p2 = _make_payload("box1", timestamp="2024-01-01T00:00:01.000Z")
        self.assertEqual(_canonical_payload(p1), _canonical_payload(p2))

    def test_different_data_not_equal(self):
        p1 = _make_payload("box1", color="#ff0000")
        p2 = _make_payload("box1", color="#00ff00")
        self.assertNotEqual(_canonical_payload(p1), _canonical_payload(p2))

    def test_invalid_json_passthrough(self):
        raw = "not-json"
        self.assertEqual(_canonical_payload(raw), raw)

    def test_no_timestamp_field_is_fine(self):
        payload = json.dumps({"object_id": "x", "action": "create"})
        canonical = _canonical_payload(payload)
        parsed = json.loads(canonical)
        self.assertEqual(parsed["object_id"], "x")


class TestPublishThrottleDuplicateSuppression(unittest.TestCase):
    def setUp(self):
        self.throttle = PublishThrottle()

    def test_first_publish_allowed(self):
        payload = _make_payload("box1")
        allowed, warning = self.throttle.check("box1", payload)
        self.assertTrue(allowed)
        self.assertIsNone(warning)

    def test_same_payload_twice_suppressed(self):
        payload = _make_payload("box1", timestamp="t1")
        self.throttle.check("box1", payload)
        # Same content, different timestamp – still a duplicate
        payload2 = _make_payload("box1", timestamp="t2")
        allowed, warning = self.throttle.check("box1", payload2)
        self.assertFalse(allowed)
        self.assertIn("duplicate", warning.lower())
        self.assertIn("box1", warning)

    def test_changed_payload_allowed_after_duplicate(self):
        payload1 = _make_payload("box1", color="#ff0000")
        self.throttle.check("box1", payload1)
        # Change the data
        payload2 = _make_payload("box1", color="#00ff00")
        allowed, warning = self.throttle.check("box1", payload2)
        self.assertTrue(allowed)
        self.assertIsNone(warning)

    def test_different_object_ids_independent(self):
        payload = _make_payload("box1")
        self.throttle.check("box1", payload)
        # Same payload structure but different object_id
        payload_b = _make_payload("box2")
        allowed, warning = self.throttle.check("box2", payload_b)
        self.assertTrue(allowed)
        self.assertIsNone(warning)

    def test_none_object_id_always_allowed(self):
        payload = _make_payload("box1")
        allowed, warning = self.throttle.check(None, payload)
        self.assertTrue(allowed)
        self.assertIsNone(warning)

    def test_empty_string_object_id_always_allowed(self):
        payload = _make_payload("box1")
        allowed, _ = self.throttle.check("", payload)
        self.assertTrue(allowed)


class TestPublishThrottleRateLimiting(unittest.TestCase):
    def setUp(self):
        self.throttle = PublishThrottle()

    def _flood_object(self, object_id, count, distinct=True):
        """Publish `count` distinct payloads for object_id (to avoid duplicate suppression)."""
        results = []
        for i in range(count):
            payload = _make_payload(object_id, color=f"#{i:06x}" if distinct else "#ffffff")
            results.append(self.throttle.check(object_id, payload))
        return results

    def test_below_rate_limit_all_allowed(self):
        results = self._flood_object("obj1", RATE_LIMIT)
        for allowed, _ in results:
            self.assertTrue(allowed)

    def test_over_rate_limit_suppressed(self):
        # First RATE_LIMIT messages should be allowed (distinct payloads)
        for i in range(RATE_LIMIT):
            allowed, _ = self.throttle.check("obj2", _make_payload("obj2", color=f"#{i:06x}"))
            self.assertTrue(allowed, f"Message {i} should be allowed")
        # The next one should be denied
        allowed, warning = self.throttle.check("obj2", _make_payload("obj2", color="#abcdef"))
        self.assertFalse(allowed)
        self.assertIn("rate", warning.lower())
        self.assertIn("obj2", warning)

    def test_rate_limit_resets_after_window(self):
        """After the window expires, rate counter should reset."""
        # Fill to limit
        for i in range(RATE_LIMIT):
            self.throttle.check("obj3", _make_payload("obj3", color=f"#{i:06x}"))

        # Manually rewind all stored timestamps past the window
        q = self.throttle._timestamps["obj3"]
        past = time.time() - WINDOW_SECS - 1.0
        for idx in range(len(q)):
            q[idx] = past

        # Now a new message should be allowed
        allowed, warning = self.throttle.check("obj3", _make_payload("obj3", color="#ffffff"))
        self.assertTrue(allowed)
        self.assertIsNone(warning)

    def test_rate_limit_per_object_independent(self):
        """Rate limit for one object_id should not affect another."""
        # Exceed limit on obj4
        for i in range(RATE_LIMIT):
            self.throttle.check("obj4", _make_payload("obj4", color=f"#{i:06x}"))
        # obj5 is still fresh
        allowed, _ = self.throttle.check("obj5", _make_payload("obj5"))
        self.assertTrue(allowed)


class TestPublishThrottleIntegration(unittest.TestCase):
    """Integration: duplicate check takes priority before rate check."""

    def test_duplicate_checked_before_rate(self):
        throttle = PublishThrottle()
        payload = _make_payload("box1", timestamp="t1")
        throttle.check("box1", payload)
        # Second call: same payload, different timestamp (still duplicate)
        payload2 = _make_payload("box1", timestamp="t2")
        allowed, warning = throttle.check("box1", payload2)
        self.assertFalse(allowed)
        # Warning should be about duplicate, not rate
        self.assertIn("duplicate", warning.lower())


if __name__ == "__main__":
    unittest.main()
