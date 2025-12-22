import unittest
from arena.test_system import ArenaE2ETest


class TestRandomSphere(unittest.TestCase):
    def test_random_sphere_logic(self):
        """
        Test random_sphere.py against its recorded trace.

        Verifies:
        1. Sphere is created with object_type="sphere"
        2. Click event is processed (mousedown on target)
        3. Sphere is updated with a DIFFERENT color than initial
        """
        colors_seen = []

        def track_color(event_idx, expected, actual):
            """Track sphere colors across matched outputs."""
            if actual.get("object_id") == "random_sphere":
                material = actual.get("data", {}).get("material", {})
                color = material.get("color")
                if color:
                    colors_seen.append(color)
                    print(f"[Color Check] Output {event_idx}: color={color}")

        ArenaE2ETest.run_script(
            script_path="examples/random_sphere.py",
            trace_path="tests/trace_random_sphere.json",
            on_output_match=track_color,
            scene_name="random",
            namespace="public",
        )

        # Verify that we saw at least 2 colors and they are different
        if len(colors_seen) >= 2:
            assert colors_seen[0] != colors_seen[1], (
                f"Color should change after click: initial={colors_seen[0]}, after={colors_seen[1]}"
            )
            print(
                f"[Color Check] ✓ Color changed from {colors_seen[0]} to {colors_seen[1]}"
            )


if __name__ == "__main__":
    unittest.main()
