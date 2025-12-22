# ARENA-py Testing Infrastructure

This directory contains the testing infrastructure for ARENA-py, enabling End-to-End (E2E) testing without requiring a live MQTT broker or network connection.

## Overview

The testing system uses a **Mock Transport** layer to simulate MQTT communication. This allows you to:
1.  **Inject** incoming messages (simulating other clients or the server).
2.  **Capture** outgoing messages (verifying your script's behavior).
3.  **Mocks** authentication and persistence calls for a completely offline environment.

## Running Tests

You can run existing tests using unittest:

```bash
python -m unittest discover tests
```

To run a specific test:

```bash
python tests/test_e2e.py
```

## Creating New Tests

We provide the `ArenaE2ETest` harness class in `arena.test_system`.

### Basic Template

```python
import unittest
from arena.test_system import ArenaE2ETest

class TestMyFeature(unittest.IsolatedAsyncioTestCase):
    async def test_my_logic(self):
        # 1. Initialize Harness
        harness = ArenaE2ETest(scene_name="test", namespace="public")
        
        # 2. Inject Setup Messages (optional)
        # Simulate an object already existing
        harness.inject_message("realm/s/public/test/o/box", {
            "object_id": "box", "action": "create", "type": "object", "data": {...}
        })
        
        # 3. Modify Scene (Your Code Under Test)
        # direct access to harness.scene
        harness.scene.add_object(Box(object_id="my_box"))
        
        # 4. Assert Output
        msgs = harness.capture_published_messages()
        self.assertTrue(any(m['payload']['object_id'] == "my_box" for m in msgs))
```

### Script Verification (Trace Driven)

The recommended way to test scripts is using **Trace Verification**.
1. Verify the script behaves correctly manually while recording a trace (env `ARENA_RECORD_TRACE=1`).
2. Run the test harness against this trace using `verify_trace`.

```python
    async def test_trace(self):
         harness = ArenaE2ETest(scene_name="scene", namespace="namespace")
         # Intercept scene, run script...
         await harness.verify_trace("trace.json")
```

This ensures that:
- Every `output` in the trace is produced by the script (with matching payload).
- Every `input` in the trace is injected into the script at the appropriate time (after preceding outputs are verified).

### Manual Script Verification

To verify an existing script manually:
1.  **Mock the Scene**: Use `unittest.mock.patch` to intercept the script's `Scene` creation and route it to your harness.
2.  **Import the Script**: Importing runs the script logic.
3.  **Inject and Assert**: Use `harness.inject_message` to simulate user actions (like clicks) and check for expected responses.
    *   *See `tests/test_random_sphere.py` for a complete example.*

## Record and Replay

You can capture "traces" from a real live session and use them for regression testing.

### 1. Recording
Run your script with `ARENA_RECORD_TRACE=1`. This will generate `mqtt_trace.json`.

```bash
export ARENA_RECORD_TRACE=1
python examples/my_script.py
```

### 2. Replaying
The replay runner will re-inject the inputs recorded in the trace.

```bash
export ARENA_TRACE_FILE=mqtt_trace.json
python tests/test_replay.py
```

Note: Replaying checks that the script doesn't crash but does not automatically verify complex logic unless extended.

## Key Components

*   **`arena/transport.py`**: Defines the `Transport` interface, `PahoMQTTTransport` (production), and `MockMQTTTransport` (testing).
*   **`arena/test_system.py`**: Defines `ArenaE2ETest`, which sets up a `Scene` with the mock transport and default configuration.
