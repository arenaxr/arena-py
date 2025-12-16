import asyncio
import json
import os
from unittest.mock import MagicMock
from .scene import Scene
from .transport import MockMQTTTransport

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

    async def verify_trace(self, trace_path : str):
        """
        Verifies execution against a recorded trace.
        - 'output' events in trace are expected to be published by the scene.
        - 'input' events in trace are injected into the scene.
        """
        import json
        with open(trace_path, 'r') as f:
            events = json.load(f)
            
        print(f"[Verify] Loaded {len(events)} events from {trace_path}")
        
        # Cursor for our captured messages
        captured_idx = 0
        
        for i, event in enumerate(events):
            if event['type'] == 'input':
                print(f"[Verify] Step {i}: Injecting input {event['topic']}")
                
                # Ensure subscriptions are active before injecting first message
                if i == 0 or not self.transport.subscriptions:
                    pass # Wait for subscriptions check (simplified logic)
                    for _ in range(5): 
                        if self.transport.subscriptions: break
                        await self.run_step(0.1)

                self.inject_message(event['topic'], event['payload'])
                # Give time for processing
                await self.run_step(0.1)
                
            elif event['type'] == 'output':
                print(f"[Verify] Step {i}: Expecting output {event['topic']}")
                
                # We need to find this message in our captured list.
                # We search from captured_idx onwards.
                # We might need to wait if it hasn't arrived yet.
                found = False
                attempts = 0
                max_attempts = 20 # 2 seconds
                
                while not found and attempts < max_attempts:
                    current_msgs = self.transport.published_messages
                    
                    # Search new messages
                    for idx in range(captured_idx, len(current_msgs)):
                        msg = current_msgs[idx]
                        
                        # Match logic: Topic must match. Payload must match subset.
                        # Trace payload might be partial or full.
                        # For simple verification, let's match action and object_id if present.
                        
                        trace_payload = event['payload']
                        actual_payload = msg['payload']
                        if isinstance(actual_payload, bytes): actual_payload = actual_payload.decode('utf-8')
                        if isinstance(actual_payload, str):
                            try: actual_payload = json.loads(actual_payload)
                            except: pass

                        # Relaxed Topic Match:
                        # Topics often contain session-specific IDs (e.g. .../o/Ivan_34823_py/object).
                        # We match if:
                        # 1. Exact topic match.
                        # 2. Suffix match on '/{object_id}' (if object_id is known).
                        topic_match = (msg['topic'] == event['topic'])
                        if not topic_match and 'object_id' in trace_payload:
                             obj_id = trace_payload['object_id']
                             if msg['topic'].endswith(f"/{obj_id}") and event['topic'].endswith(f"/{obj_id}"):
                                 topic_match = True
                        
                        if not topic_match: continue

                        # Payload Verification: Check critical keys (action, object_id, type)
                        match = True
                        if isinstance(trace_payload, dict) and isinstance(actual_payload, dict):
                            for key in ['action', 'object_id', 'type']:
                                if key in trace_payload:
                                    if trace_payload[key] != actual_payload.get(key):
                                        match = False
                                        break
                            # Also check 'data' subset if present?
                            if match and 'data' in trace_payload and 'data' in actual_payload:
                                # Start simplified: if trace has object_type, match it
                                if 'object_type' in trace_payload['data']:
                                    if trace_payload['data']['object_type'] != actual_payload['data'].get('object_type'):
                                        match = False
                        
                        if match:
                            found = True
                            captured_idx = idx + 1 # Advance cursor
                            print(f"[Verify]   Matched message index {idx}")
                            break
                    
                    if not found:
                        await self.run_step(0.1)
                        attempts += 1
                        
                if not found:
                    raise AssertionError(f"Step {i} Failed: Expected output {event['topic']} with payload {event['payload']} not found within timeout.")
