import unittest
import os
from arena.test_system import ArenaE2ETest


class TestArenaReplay(unittest.IsolatedAsyncioTestCase):
    async def test_replay_trace(self):
        """
        Replay a recorded trace file and verify outputs match.
        Set ARENA_TRACE_FILE env var to specify trace file path.
        """
        trace_file = os.environ.get("ARENA_TRACE_FILE", "mqtt_trace.json")
        if not os.path.exists(trace_file):
            self.skipTest(f"No trace file found at {trace_file}")

        harness = ArenaE2ETest(scene_name="test_scene", realm="realm", namespace="user")
        await harness.verify_trace(trace_file)


if __name__ == '__main__':
    unittest.main()
