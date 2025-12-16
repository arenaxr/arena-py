import json
import unittest
import sys
import os
import asyncio
from arena.test_system import ArenaE2ETest
from arena.objects import Object

class TestArenaE2E(unittest.IsolatedAsyncioTestCase):
    async def test_e2e_flow(self):
        """
        Demonstrates a manual E2E test without using a trace file.
        Useful for programmatic verification of features.
        """
        # 1. Initialize Harness
        harness = ArenaE2ETest(scene_name="test_scene", realm="realm", namespace="user")
        print(f"\n[Test] Harness started. Mock Scene: {harness.scene_name}")
        
        # 2. Script Action: Create Object
        # We simulate the script logic directly here
        print("[Test] Script Action: create object box1")
        box = Object(object_id="box1", object_type="box", position={"x":0, "y":1, "z":-2})
        harness.scene.add_object(box)
        
        # 3. Wait for network simulation
        print("[Test] Sleeping 0.1s...")
        await harness.run_step(0.1)
        
        # 4. Verify Output
        print("[Test] Verifying output...")
        published = harness.capture_published_messages()
        
        # Look for the creation message
        found_msg = None
        for msg in published:
            # Decode payload
            payload = msg['payload']
            if isinstance(payload, bytes): payload = payload.decode('utf-8')
            if isinstance(payload, str):
                try: payload = json.loads(payload)
                except: pass
                
            if isinstance(payload, dict):
                if payload.get('object_id') == "box1" and payload.get('action') == "create":
                    found_msg = payload
                    break
        
        if found_msg:
            print(f"[Test] Found expected message: {found_msg}")
        else:
            print(f"[Test] FAILED: Did not find creation message for box1")
            
        self.assertIsNotNone(found_msg, "Expected creation message for box1 not found")
        self.assertEqual(found_msg['data']['object_type'], "box")

if __name__ == '__main__':
    unittest.main()
