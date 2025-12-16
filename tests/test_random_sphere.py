import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import json
import asyncio

# Add examples to path so we can import random_sphere
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'examples')))

from arena.test_system import ArenaE2ETest
from arena.transport import MockMQTTTransport
from arena.objects import Object

class TestRandomSphere(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Clear global object registry to ensure clean state
        Object.all_objects = {}
        Object.private_objects = {}

    async def test_random_sphere_logic(self):
        # 1. Setup the Harness (Mock Transport, etc)
        # We need to bridge the script's Scene instantiation to our harness.
        # The script does: scene = Scene(...)
        
        # We'll create our harness first.
        harness = ArenaE2ETest(scene_name="random", namespace="public")
        harness.scene.debug = True # Enable debug to trace message processing
        
        # Bridge script's Scene instantiation to our harness
        
        with patch('arena.Scene') as MockSceneClass:
            # Mock Scene methods to prevent actual execution blocking
            MockSceneClass.return_value = harness.scene
            harness.scene.run_tasks = MagicMock()
            
            # 2. Run the script
            import random_sphere
            
            # 3. Verify Execution against Trace
            try:
                # Need to use absolute path or relative to CWD if running from root
                await harness.verify_trace("tests/trace_random_sphere.json")
            except AssertionError as e:
                self.fail(f"Trace verification failed: {e}")

if __name__ == '__main__':
    unittest.main()
