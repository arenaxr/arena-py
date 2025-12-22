import asyncio
import json
import os
from unittest.mock import MagicMock
from .scene import Scene
from .transport import MockMQTTTransport

# Fields to ignore when comparing payloads (dynamic/timing-related)
IGNORE_FIELDS = {'timestamp', 'time', 'ts', 'lastUpdated', 'createdAt', 'updatedAt'}


def payloads_match(expected, actual, path=""):
    """
    Recursively compare two payloads, ignoring timestamp fields.
    Returns (match: bool, diff_description: str or None)
    """
    # Normalize: if either is bytes, decode
    if isinstance(expected, bytes):
        expected = json.loads(expected.decode('utf-8'))
    if isinstance(actual, bytes):
        actual = json.loads(actual.decode('utf-8'))
    if isinstance(expected, str):
        try: expected = json.loads(expected)
        except json.JSONDecodeError: pass
    if isinstance(actual, str):
        try: actual = json.loads(actual)
        except json.JSONDecodeError: pass
    
    # If both are dicts, compare keys
    if isinstance(expected, dict) and isinstance(actual, dict):
        for key in expected:
            if key in IGNORE_FIELDS:
                continue
            if key not in actual:
                return False, f"{path}.{key}: missing in actual"
            match, diff = payloads_match(expected[key], actual[key], f"{path}.{key}")
            if not match:
                return False, diff
        return True, None
    
    # If both are lists, compare element-wise
    if isinstance(expected, list) and isinstance(actual, list):
        if len(expected) != len(actual):
            return False, f"{path}: list length mismatch ({len(expected)} vs {len(actual)})"
        for i, (e, a) in enumerate(zip(expected, actual)):
            match, diff = payloads_match(e, a, f"{path}[{i}]")
            if not match:
                return False, diff
        return True, None
    
    # Direct comparison for primitives
    if expected != actual:
        return False, f"{path}: {expected!r} != {actual!r}"
    
    return True, None


class ArenaE2ETest:
    def __init__(self, scene_name="test_scene", namespace="user", realm="realm"):
        # Mock auth to avoid network calls
        os.environ["ARENA_USERNAME"] = "test_user"
        # minimal valid jwt structure: header.payload.signature
        # {"exp": 1735689600, "publ": ["#"], "subl": ["#"]} base64 encoded
        os.environ["ARENA_PASSWORD"] = "eyJhIjogMX0=.eyJleHAiOiAxNzM1Njg5NjAwLCAicHVibCI6IFsiIyJdLCAic3VibCI6IFsiIyJdfQ==.signature"

        # Create mock transport
        self.transport = MockMQTTTransport("test_client")
        self.scene_name = scene_name
        
        # Instantiate scene with mock transport; process headless to avoid user auth interactions
        self.scene = Scene(
            host="example.com",
            realm=realm,
            namespace=namespace,
            scene=scene_name,
            transport=self.transport,
            headless=True,
            config_data={
                "ARENADefaults": {
                    "mqttHost": "mqtt.example.com",
                    "latencyTopic": "$NETWORK/latency",
                    "persistHost": "persist.example.com",
                    "persistPath": "/persist/",
                    "realm": "realm",
                    "namespace": "public",
                    "sceneName": "lobby",
                    "graphTopic": "$NETWORK",
                    "camUpdateIntervalMs": 100,
                    "userName": "Anonymous",
                    "startCoords": {"x": 0, "y": 0, "z": 0},
                    "camHeight": 1.6,
                    "vioTopic": "/topic/vio/",
                    "headModelPath": "/static/models/avatars/robobit.glb"
                }
            } 
        )

        # Mock auth.urlopen to return persist data
        # Data provided by user example
        persist_data = [
            {"object_id": "lobby-model", "attributes": {"object_type": "gltf-model", "position": {"x": 0, "y": -2, "z": 0}}, "type": "object"},
            {"object_id": "start", "attributes": {"object_type": "cube", "position": {"x": 18, "y": -2, "z": 11.5}}, "type": "object"}
        ]
        self.scene.auth.urlopen = MagicMock(return_value=json.dumps(persist_data))
        
        # Start tasks manually since we won't call run_forever
        self._start_tasks()
        
    def _start_tasks(self):
        """Manually start the background tasks of the scene."""
        current_loop = asyncio.get_event_loop()
        # Verify if scene loop is same as current loop
        if self.scene.event_loop.loop is not current_loop:
            pass
            
        for task in self.scene.event_loop.tasks:
             asyncio.create_task(task)

    def inject_message(self, topic, payload):
        """Injects a message as if received from MQTT."""
        # payload is a dict, we convert to bytes for mock transport
        payload_bytes = json.dumps(payload).encode('utf-8')
        self.transport.mock_receive(topic, payload_bytes)
        
    async def run_step(self, duration=0.1):
        """Runs the event loop for a short duration."""
        await asyncio.sleep(duration)
        
    def capture_published_messages(self):
        """Returns list of published messages."""
        return self.transport.published_messages

    async def verify_trace(self, trace_path: str):
        """
        Verifies execution against a recorded trace.
        
        Sequencing:
        - 'output' events are batched until the next 'input' or end of trace
        - All expected outputs in a batch are verified before injecting the next input
        - This maintains proper causality for interactive programs
        """
        with open(trace_path, 'r') as f:
            events = json.load(f)
            
        print(f"[Verify] Loaded {len(events)} events from {trace_path}")
        
        # Group events into batches: each batch is (optional input, [outputs])
        # This allows us to verify all outputs triggered by an input before moving on
        batches = []
        current_outputs = []
        
        for event in events:
            if event['type'] == 'input':
                # If we have pending outputs, they belong to the previous batch (or initial state)
                if current_outputs:
                    batches.append((None, current_outputs))
                    current_outputs = []
                # Start a new batch with this input
                batches.append((event, []))
            elif event['type'] == 'output':
                # Add to current batch's outputs
                if batches and batches[-1][0] is not None:
                    # Append to the last input's outputs
                    batches[-1][1].append(event)
                else:
                    # Output before any input (initial outputs)
                    current_outputs.append(event)
        
        # Don't forget trailing outputs
        if current_outputs:
            batches.append((None, current_outputs))
        
        # Track which captured messages we've already matched
        matched_indices = set()
        
        for batch_idx, (input_event, expected_outputs) in enumerate(batches):
            # 1. First verify any expected outputs from previous input (or initial state)
            if expected_outputs:
                print(f"[Verify] Batch {batch_idx}: Expecting {len(expected_outputs)} output(s)")
                
                # Wait and verify all expected outputs
                await self._verify_outputs(expected_outputs, matched_indices)
            
            # 2. Then inject the input (if any)
            if input_event:
                print(f"[Verify] Batch {batch_idx}: Injecting input {input_event['topic']}")
                
                # Ensure subscriptions are active before first injection
                if batch_idx == 0 or not self.transport.subscriptions:
                    for _ in range(5):
                        if self.transport.subscriptions: break
                        await self.run_step(0.1)
                
                self.inject_message(input_event['topic'], input_event['payload'])
                await self.run_step(0.1)
        
        print("[Verify] Trace verification complete - all outputs matched.")

    async def _verify_outputs(self, expected_outputs: list, matched_indices: set):
        """Verify a batch of expected outputs, waiting for them to appear."""
        for i, event in enumerate(expected_outputs):
            expected_payload = event['payload']
            found = False
            attempts = 0
            max_attempts = 20  # 2 seconds total
            best_diff = None
            
            while not found and attempts < max_attempts:
                current_msgs = self.transport.published_messages
                
                for idx in range(len(current_msgs)):
                    if idx in matched_indices:
                        continue
                    
                    msg = current_msgs[idx]
                    match, diff = payloads_match(expected_payload, msg['payload'])
                    
                    if match:
                        found = True
                        matched_indices.add(idx)
                        print(f"[Verify]   ✓ Output {i}: Matched message [{idx}]")
                        break
                    else:
                        if best_diff is None:
                            best_diff = diff
                
                if not found:
                    await self.run_step(0.1)
                    attempts += 1
            
            if not found:
                raise AssertionError(
                    f"Output verification failed for: {event['topic']}\n"
                    f"Expected payload: {json.dumps(expected_payload, indent=2)}\n"
                    f"Captured {len(self.transport.published_messages)} message(s), none matched.\n"
                    f"Closest diff: {best_diff}"
                )

