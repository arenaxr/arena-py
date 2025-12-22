import asyncio
import importlib.util
import json
import os
import sys
from unittest.mock import MagicMock, patch
from .scene import Scene
from .transport import MockMQTTTransport
from .objects import Object

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
            {"object_id": "start", "attributes": {"object_type": "box", "position": {"x": 18, "y": -2, "z": 11.5}}, "type": "object"}
        ]
        self.scene.auth.urlopen = MagicMock(return_value=json.dumps(persist_data))
        
        # Tasks will be started when entering async context
        self._tasks_started = False
        
    def _start_tasks(self):
        """Start background tasks of the scene. Must be called from async context."""
        if self._tasks_started:
            return
        self._tasks_started = True
        
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

    async def verify_trace(self, trace_path: str, on_output_match=None, on_any_output=None):
        """
        Verifies execution against a recorded trace.
        
        Args:
            trace_path: Path to the trace JSON file
            on_output_match: Callback(event_idx, expected, actual) called when an output matches
            on_any_output: Callback(actual) called for every captured output
        
        Sequencing:
        - 'output' events are batched until the next 'input' or end of trace
        - All expected outputs in a batch are verified before injecting the next input
        - This maintains proper causality for interactive programs
        """
        # Start background tasks now that we're in async context
        self._start_tasks()
        
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
            if input_event is None:
                # Initial outputs - verify them first (no input to trigger)
                if expected_outputs:
                    print(f"[Verify] Batch {batch_idx}: Expecting {len(expected_outputs)} initial output(s)")
                    await self._verify_outputs(expected_outputs, matched_indices, on_output_match, on_any_output)
            else:
                # Input batch: inject input FIRST, then verify outputs it triggers
                print(f"[Verify] Batch {batch_idx}: Injecting input {input_event['topic']}")
                
                # Ensure subscriptions are active before first injection
                if not self.transport.subscriptions:
                    for _ in range(5):
                        if self.transport.subscriptions: break
                        await self.run_step(0.1)
                
                self.inject_message(input_event['topic'], input_event['payload'])
                await self.run_step(0.1)
                
                # Now verify the outputs triggered by this input
                if expected_outputs:
                    print(f"[Verify] Batch {batch_idx}: Expecting {len(expected_outputs)} output(s)")
                    await self._verify_outputs(expected_outputs, matched_indices, on_output_match, on_any_output)
        
        print("[Verify] Trace verification complete - all outputs matched.")

    async def _verify_outputs(self, expected_outputs: list, matched_indices: set, 
                              on_output_match=None, on_any_output=None):
        """Verify a batch of expected outputs, waiting for them to appear.
        
        Args:
            expected_outputs: List of expected output events from trace
            matched_indices: Set of already-matched message indices
            on_output_match: Callback(event_idx, expected, actual) on match
            on_any_output: Callback(actual) for each captured output
        """
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
                    actual_payload = msg['payload']
                    
                    # Ensure actual_payload is parsed (may be JSON string)
                    if isinstance(actual_payload, str):
                        try:
                            actual_payload = json.loads(actual_payload)
                        except json.JSONDecodeError:
                            pass  # Keep as string if not valid JSON
                    
                    # Call on_any_output for every output we see (first time)
                    if on_any_output and idx not in matched_indices:
                        try:
                            on_any_output(actual_payload)
                        except Exception as e:
                            raise AssertionError(f"on_any_output callback failed for message {idx}: {e}")
                    
                    match, diff = payloads_match(expected_payload, actual_payload)
                    
                    if match:
                        found = True
                        matched_indices.add(idx)
                        print(f"[Verify]   ✓ Output {i}: Matched message [{idx}]")
                        
                        # Call on_output_match callback
                        if on_output_match:
                            try:
                                on_output_match(i, expected_payload, actual_payload)
                            except Exception as e:
                                raise AssertionError(f"on_output_match callback failed for output {i}: {e}")
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

    @classmethod
    def run_script(cls, script_path: str, trace_path: str, 
                   on_output_match=None, on_any_output=None, **scene_kwargs) -> bool:
        """
        Load and test an existing script against a recorded trace.
        
        Args:
            script_path: Path to the Python script (e.g., 'examples/random_sphere.py')
            trace_path: Path to the recorded trace JSON file
            on_output_match: Callback(event_idx, expected, actual) called when output matches
            on_any_output: Callback(actual) called for every captured output
            **scene_kwargs: Override scene parameters (scene_name, namespace, realm)
        
        Returns:
            True if verification passed, raises AssertionError otherwise
        
        Usage:
            ArenaE2ETest.run_script('examples/random_sphere.py', 'traces/random_sphere.json')
        """
        # Extract scene params from trace or use defaults
        scene_name = scene_kwargs.get('scene_name', 'test_scene')
        namespace = scene_kwargs.get('namespace', 'public')
        realm = scene_kwargs.get('realm', 'realm')
        
        # Ensure a fresh event loop exists (asyncio.run closes the loop after each call)
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # No running loop - create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Clear global object registry for clean state
        Object.all_objects = {}
        Object.private_objects = {}
        
        # Create harness with mock transport
        harness = cls(scene_name=scene_name, namespace=namespace, realm=realm)
        
        # Make run_tasks() a no-op so script doesn't block
        original_run_tasks = harness.scene.run_tasks
        harness.scene.run_tasks = lambda: None
        
        # Add script's directory to path so relative imports work
        script_dir = os.path.dirname(os.path.abspath(script_path))
        if script_dir not in sys.path:
            sys.path.insert(0, script_dir)
        
        try:
            # Create a Scene factory that returns our harness scene
            def mock_scene_factory(*args, **kwargs):
                return harness.scene
            
            # Build a namespace with all arena exports, plus our mock Scene
            import arena
            import arena.objects
            import arena.attributes
            script_globals = {}
            
            # Copy all arena exports (including submodule exports)
            for mod in [arena, arena.objects, arena.attributes]:
                for name in dir(mod):
                    if not name.startswith('_'):
                        script_globals[name] = getattr(mod, name)
            
            # Override Scene with our mock
            script_globals['Scene'] = mock_scene_factory
            
            # Add builtins
            script_globals['__builtins__'] = __builtins__
            script_globals['__name__'] = '__main__'
            script_globals['__file__'] = script_path
            
            try:
                # Load and execute the script with our prepared namespace
                print(f"[Test] Loading script: {script_path}")
                with open(script_path, 'r') as f:
                    script_code = f.read()
                
                exec(compile(script_code, script_path, 'exec'), script_globals)
                print(f"[Test] Script loaded. Objects created: {len(Object.all_objects)}")
            except SystemExit:
                pass  # Script may call sys.exit() or similar
            
            # Now verify against trace
            async def _verify():
                await harness.verify_trace(trace_path, on_output_match, on_any_output)
            
            asyncio.run(_verify())
            print(f"[Test] ✓ {script_path} passed verification")
            return True
            
        finally:
            # Restore run_tasks
            harness.scene.run_tasks = original_run_tasks
            # Clean up sys.path
            if script_dir in sys.path:
                sys.path.remove(script_dir)

    @classmethod
    def run_test_suite(cls, test_cases: list) -> dict:
        """
        Run multiple script tests and report results.
        
        Args:
            test_cases: List of dicts with 'script', 'trace', and optional scene kwargs
                Example: [
                    {'script': 'examples/random_sphere.py', 'trace': 'traces/random_sphere.json'},
                    {'script': 'examples/box_click.py', 'trace': 'traces/box_click.json', 'scene_name': 'click'},
                ]
        
        Returns:
            Dict with 'passed', 'failed', and 'results' keys
        """
        results = {'passed': 0, 'failed': 0, 'results': []}
        
        for i, test_case in enumerate(test_cases):
            script = test_case['script']
            trace = test_case['trace']
            kwargs = {k: v for k, v in test_case.items() if k not in ('script', 'trace')}
            
            print(f"\n{'='*60}")
            print(f"[Suite] Test {i+1}/{len(test_cases)}: {script}")
            print('='*60)
            
            try:
                cls.run_script(script, trace, **kwargs)
                results['passed'] += 1
                results['results'].append({'script': script, 'status': 'PASSED'})
            except Exception as e:
                results['failed'] += 1
                results['results'].append({'script': script, 'status': 'FAILED', 'error': str(e)})
                print(f"[Suite] ✗ {script} FAILED: {e}")
        
        # Summary
        print(f"\n{'='*60}")
        print(f"[Suite] Results: {results['passed']} passed, {results['failed']} failed")
        print('='*60)
        
        return results
