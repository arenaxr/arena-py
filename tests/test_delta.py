"""Tests for delta compression (arena.delta.deep_diff)."""

import json
import unittest

from arena.delta import deep_diff


class TestDeepDiff(unittest.TestCase):
    """Unit tests for deep_diff function."""

    def test_identical_objects(self):
        """Identical dicts should produce empty diff."""
        d = {"position": {"x": 1, "y": 2, "z": 3}, "color": "#ff0000"}
        self.assertEqual(deep_diff(d, d.copy()), {})

    def test_position_change(self):
        """Only changed position fields should appear in diff."""
        prev = {"position": {"x": 2.965, "y": 1.6, "z": 8.877}, "rotation": {"w": 1, "x": 0, "y": 0, "z": 0}}
        next_val = {"position": {"x": 2.852, "y": 1.6, "z": 8.88}, "rotation": {"w": 1, "x": 0, "y": 0, "z": 0}}
        diff = deep_diff(prev, next_val)
        self.assertEqual(diff, {"position": {"x": 2.852, "z": 8.88}})
        self.assertNotIn("rotation", diff)

    def test_camera_sequence(self):
        """Full camera message delta from spec — only position.x and position.z changed."""
        prev_data = {
            "arena-user": {
                "color": "#eca7ef",
                "displayName": "Ivan",
                "hasAudio": False,
                "hasVideo": False,
                "headModelPath": "/static/models/avatars/DamagedHelmet.glb",
                "jitsiId": "7210ee23",
                "presence": "Standard",
            },
            "object_type": "camera",
            "position": {"x": 2.965, "y": 1.6, "z": 8.877},
            "rotation": {"w": 1, "x": -0.019, "y": 0.013, "z": 0},
        }
        next_data = {
            "arena-user": {
                "color": "#eca7ef",
                "displayName": "Ivan",
                "hasAudio": False,
                "hasVideo": False,
                "headModelPath": "/static/models/avatars/DamagedHelmet.glb",
                "jitsiId": "7210ee23",
                "presence": "Standard",
            },
            "object_type": "camera",
            "position": {"x": 2.852, "y": 1.6, "z": 8.88},
            "rotation": {"w": 1, "x": -0.019, "y": 0.013, "z": 0},
        }
        diff = deep_diff(prev_data, next_data)
        self.assertEqual(diff, {"position": {"x": 2.852, "z": 8.88}})

        # Verify the delta is much smaller than the full payload
        full_size = len(json.dumps(next_data))
        delta_size = len(json.dumps(diff))
        self.assertLess(delta_size, full_size / 2)

    def test_null_component_delete(self):
        """None value (semantic delete) must flow through the diff."""
        prev = {"object_type": "box", "material": {"color": "#ff0000"}}
        next_val = {"object_type": "box", "material": None}
        diff = deep_diff(prev, next_val)
        self.assertEqual(diff, {"material": None})

    def test_null_to_null_noop(self):
        """Both prev and next have None for same key → omitted from diff."""
        prev = {"object_type": "box", "material": None}
        next_val = {"object_type": "box", "material": None}
        diff = deep_diff(prev, next_val)
        self.assertEqual(diff, {})

    def test_new_field_added(self):
        """Field in next but not prev should be included."""
        prev = {"object_type": "box"}
        next_val = {"object_type": "box", "material": {"color": "#00ff00"}}
        diff = deep_diff(prev, next_val)
        self.assertEqual(diff, {"material": {"color": "#00ff00"}})

    def test_field_removed(self):
        """Field in prev but not next → emitted as None (semantic delete)."""
        prev = {"object_type": "box", "material": {"color": "#ff0000"}}
        next_val = {"object_type": "box"}
        diff = deep_diff(prev, next_val)
        self.assertEqual(diff, {"material": None})

    def test_nested_partial_change(self):
        """Only changed fields in nested dicts should appear."""
        prev = {"material": {"color": "#ff0000", "opacity": 0.5, "transparent": True}}
        next_val = {"material": {"color": "#00ff00", "opacity": 0.5, "transparent": True}}
        diff = deep_diff(prev, next_val)
        self.assertEqual(diff, {"material": {"color": "#00ff00"}})

    def test_array_unchanged(self):
        """Identical arrays should be omitted from diff."""
        prev = {"path": [[0, 0, 0], [1, 1, 1]], "object_type": "line"}
        next_val = {"path": [[0, 0, 0], [1, 1, 1]], "object_type": "line"}
        diff = deep_diff(prev, next_val)
        self.assertEqual(diff, {})

    def test_array_changed(self):
        """Changed arrays should be included in diff."""
        prev = {"path": [[0, 0, 0], [1, 1, 1]]}
        next_val = {"path": [[0, 0, 0], [2, 2, 2]]}
        diff = deep_diff(prev, next_val)
        self.assertEqual(diff, {"path": [[0, 0, 0], [2, 2, 2]]})

    def test_deep_nested_diff(self):
        """3+ levels of nesting should be handled correctly."""
        prev = {"a": {"b": {"c": {"d": 1, "e": 2}}, "f": 3}}
        next_val = {"a": {"b": {"c": {"d": 1, "e": 99}}, "f": 3}}
        diff = deep_diff(prev, next_val)
        self.assertEqual(diff, {"a": {"b": {"c": {"e": 99}}}})

    def test_empty_dicts(self):
        """Two empty dicts should produce empty diff."""
        self.assertEqual(deep_diff({}, {}), {})

    def test_prev_empty(self):
        """Empty prev means everything in next is new."""
        next_val = {"position": {"x": 1, "y": 2, "z": 3}}
        diff = deep_diff({}, next_val)
        self.assertEqual(diff, next_val)

    def test_next_empty(self):
        """Empty next means everything in prev is deleted."""
        prev = {"position": {"x": 1}, "color": "red"}
        diff = deep_diff(prev, {})
        self.assertEqual(diff, {"position": None, "color": None})

    def test_type_change_dict_to_primitive(self):
        """Dict replaced by primitive should include the new value."""
        prev = {"material": {"color": "#ff0000"}}
        next_val = {"material": "basic"}
        diff = deep_diff(prev, next_val)
        self.assertEqual(diff, {"material": "basic"})

    def test_type_change_primitive_to_dict(self):
        """Primitive replaced by dict should include the new dict."""
        prev = {"material": "basic"}
        next_val = {"material": {"color": "#ff0000"}}
        diff = deep_diff(prev, next_val)
        self.assertEqual(diff, {"material": {"color": "#ff0000"}})

    def test_bool_change(self):
        """Boolean changes should be detected."""
        prev = {"hasAudio": False, "hasVideo": False}
        next_val = {"hasAudio": True, "hasVideo": False}
        diff = deep_diff(prev, next_val)
        self.assertEqual(diff, {"hasAudio": True})

    def test_float_precision(self):
        """Float values should be compared with ==."""
        prev = {"x": 1.0}
        next_val = {"x": 1.0}
        self.assertEqual(deep_diff(prev, next_val), {})

        next_val2 = {"x": 1.0000001}
        diff = deep_diff(prev, next_val2)
        self.assertEqual(diff, {"x": 1.0000001})


class TestDeltaIntegration(unittest.TestCase):
    """Integration tests for delta compression in publish path.

    Uses Scene._apply_delta directly with crafted JSON strings to test
    the full create/update/delete lifecycle without MQTT setup.
    """

    def _make_scene(self):
        """Create a minimal mock scene with delta compression enabled."""
        import json

        class MockScene:
            delta_compression = True
            _last_published_state = {}

        # Bind _apply_delta from Scene
        from arena.scene import Scene
        scene = MockScene()
        scene._apply_delta = Scene._apply_delta.__get__(scene, MockScene)
        return scene

    def test_create_always_full(self):
        """Create action should always send full payload and store state."""
        scene = self._make_scene()
        full_msg = {
            "object_id": "box1",
            "action": "create",
            "type": "object",
            "data": {"object_type": "box", "position": {"x": 1, "y": 2, "z": 3}},
        }
        payload = json.dumps(full_msg)
        result = scene._apply_delta(payload, "create")

        # Should be unchanged (full payload)
        self.assertEqual(json.loads(result), full_msg)
        # State should be stored
        self.assertIn("box1", scene._last_published_state)

    def test_update_first_time_full(self):
        """First update for unknown object should send full."""
        scene = self._make_scene()
        msg = {
            "object_id": "box2",
            "action": "update",
            "type": "object",
            "data": {"object_type": "box", "position": {"x": 1, "y": 2, "z": 3}},
        }
        result = scene._apply_delta(json.dumps(msg), "update")
        self.assertEqual(json.loads(result), msg)
        self.assertIn("box2", scene._last_published_state)

    def test_update_with_delta(self):
        """Second update should only contain changed fields."""
        scene = self._make_scene()

        # First publish (create)
        create_msg = {
            "object_id": "cam1",
            "action": "create",
            "type": "object",
            "data": {
                "object_type": "camera",
                "position": {"x": 2.965, "y": 1.6, "z": 8.877},
                "rotation": {"w": 1, "x": -0.019, "y": 0.013, "z": 0},
            },
        }
        scene._apply_delta(json.dumps(create_msg), "create")

        # Second publish (update with only position change)
        update_msg = {
            "object_id": "cam1",
            "action": "update",
            "type": "object",
            "data": {
                "object_type": "camera",
                "position": {"x": 2.852, "y": 1.6, "z": 8.88},
                "rotation": {"w": 1, "x": -0.019, "y": 0.013, "z": 0},
            },
        }
        result = scene._apply_delta(json.dumps(update_msg), "update")
        result_msg = json.loads(result)

        # data should only have position delta
        self.assertEqual(result_msg["data"], {"position": {"x": 2.852, "z": 8.88}})
        # top-level fields preserved
        self.assertEqual(result_msg["object_id"], "cam1")
        self.assertEqual(result_msg["action"], "update")
        self.assertEqual(result_msg["type"], "object")

    def test_delete_clears_state(self):
        """Delete should clear stored state for the object."""
        scene = self._make_scene()

        # Create first
        create_msg = {
            "object_id": "box3",
            "action": "create",
            "data": {"object_type": "box"},
        }
        scene._apply_delta(json.dumps(create_msg), "create")
        self.assertIn("box3", scene._last_published_state)

        # Delete
        delete_msg = {"object_id": "box3", "action": "delete"}
        scene._apply_delta(json.dumps(delete_msg), "delete")
        self.assertNotIn("box3", scene._last_published_state)

    def test_update_after_delete_sends_full(self):
        """Update after delete should send full (no prior state)."""
        scene = self._make_scene()

        # Create, then delete
        msg = {"object_id": "box4", "action": "create", "data": {"object_type": "box", "color": "red"}}
        scene._apply_delta(json.dumps(msg), "create")
        scene._apply_delta(json.dumps({"object_id": "box4", "action": "delete"}), "delete")

        # Re-create via update
        update = {"object_id": "box4", "action": "update", "data": {"object_type": "box", "color": "blue"}}
        result = json.loads(scene._apply_delta(json.dumps(update), "update"))
        # Should be full since no prior state
        self.assertEqual(result["data"], {"object_type": "box", "color": "blue"})

    def test_no_data_field_passthrough(self):
        """Messages without data field should pass through unchanged."""
        scene = self._make_scene()
        msg = {"object_id": "x", "action": "update"}
        payload = json.dumps(msg)
        self.assertEqual(scene._apply_delta(payload, "update"), payload)

    def test_empty_delta_heartbeat(self):
        """Identical consecutive updates should produce empty data {} (heartbeat)."""
        scene = self._make_scene()

        msg = {"object_id": "hb1", "action": "create", "data": {"object_type": "box"}}
        scene._apply_delta(json.dumps(msg), "create")

        # Same data again as update
        update = {"object_id": "hb1", "action": "update", "data": {"object_type": "box"}}
        result = json.loads(scene._apply_delta(json.dumps(update), "update"))
        self.assertEqual(result["data"], {})


if __name__ == "__main__":
    unittest.main()
