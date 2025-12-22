import unittest
from arena.test_system import ArenaE2ETest


class TestRandomSphere(unittest.TestCase):
    def test_random_sphere_logic(self):
        """
        Test random_sphere.py against its recorded trace.
        
        Verifies:
        1. Sphere is created with object_type="sphere"
        2. Click event is processed (mousedown on target)
        3. Sphere is updated with a material change
        """
        ArenaE2ETest.run_script(
            script_path="examples/random_sphere.py",
            trace_path="tests/trace_random_sphere.json",
            scene_name="random",
            namespace="public"
        )


if __name__ == '__main__':
    unittest.main()
