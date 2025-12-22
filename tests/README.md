# ARENA-py Testing Infrastructure

This directory contains the testing infrastructure for ARENA-py, enabling End-to-End (E2E) testing without requiring a live MQTT broker or network connection.

## Overview

The testing system uses a **Mock Transport** layer to simulate MQTT communication. This allows you to:
1.  **Inject** incoming messages (simulating other clients or the server).
2.  **Capture** outgoing messages (verifying your script's behavior).
3.  **Mock** authentication and persistence calls for a completely offline environment.

## Running Tests

```bash
python -m unittest discover tests
```

Or run a specific test:

```bash
python tests/test_random_sphere.py
```

## Quick Start: Testing Existing Scripts

The simplest way to test an existing script is using `run_script()`:

```python
from arena.test_system import ArenaE2ETest

ArenaE2ETest.run_script(
    script_path="examples/random_sphere.py",
    trace_path="tests/trace_random_sphere.json",
    scene_name="random",
    namespace="public"
)
```

This will:
1. Load your script with a mock Scene
2. Execute the script logic
3. Replay inputs from the trace and verify outputs match

## Recording Traces

Record a trace from a live session:

```bash
export ARENA_RECORD_TRACE=1
python examples/my_script.py
# Produces: mqtt_trace.json
```

The trace captures all MQTT inputs (messages received) and outputs (messages sent).

## Trace Format

```json
[
    {"type": "output", "topic": "...", "payload": {...}},
    {"type": "input", "topic": "...", "payload": {...}},
    {"type": "output", "topic": "...", "payload": {...}}
]
```

**Verification behavior:**
- Fields in the trace are checked for **exact match** against actual output
- Empty objects `{}` act as wildcards (e.g., `"material": {}` matches any material)
- Timestamp fields are automatically ignored

## Custom Validation with Callbacks

For complex logic (e.g., verifying positions, tracking state), use callbacks:

```python
def track_position(event_idx, expected, actual):
    """Called when a trace output matches."""
    if actual.get("object_id") == "moving_box":
        pos = actual["data"]["position"]
        assert pos["x"] >= 0, "Box should stay in positive X"

ArenaE2ETest.run_script(
    script_path="examples/moving_box.py",
    trace_path="traces/moving_box.json",
    on_output_match=track_position,  # Called for matched outputs
    # on_any_output=log_all,         # Called for ALL captured outputs
)
```

**Callbacks:**
| Callback | Signature | When it fires |
|----------|-----------|---------------|
| `on_output_match` | `(event_idx, expected, actual)` | When a trace output is matched |
| `on_any_output` | `(actual)` | For every captured output message |

## Test Suite: Multiple Scripts

Test multiple scripts at once:

```python
results = ArenaE2ETest.run_test_suite([
    {"script": "examples/random_sphere.py", "trace": "traces/random_sphere.json"},
    {"script": "examples/box_click.py", "trace": "traces/box_click.json", "scene_name": "click"},
])
# results = {"passed": 2, "failed": 0, "results": [...]}
```

## Manual Testing (Advanced)

For direct control, use the harness directly:

```python
import unittest
from arena.test_system import ArenaE2ETest

class TestMyFeature(unittest.IsolatedAsyncioTestCase):
    async def test_my_logic(self):
        harness = ArenaE2ETest(scene_name="test", namespace="public")
        
        # Add objects directly
        harness.scene.add_object(Box(object_id="my_box"))
        
        # Wait for processing
        await harness.run_step(0.1)
        
        # Check outputs
        msgs = harness.capture_published_messages()
        self.assertTrue(any(m["payload"]["object_id"] == "my_box" for m in msgs))
```

## Key Components

| File | Description |
|------|-------------|
| `arena/transport.py` | `Transport` interface, `PahoMQTTTransport` (production), `MockMQTTTransport` (testing) |
| `arena/test_system.py` | `ArenaE2ETest` harness with `run_script()`, `verify_trace()`, `run_test_suite()` |
| `tests/trace_*.json` | Recorded traces for regression testing |
