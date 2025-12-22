from abc import ABC, abstractmethod
import asyncio
import paho.mqtt.client as mqtt
from paho.mqtt.client import topic_matches_sub
from .event_loop.asyncio_mqtt import AsyncioMQTTHelper
import json
import time


class Transport(ABC):
    """
    Abstract base class for MQTT Transport.
    """

    def __init__(self):
        self.on_connect = None
        self.on_disconnect = None
        self.on_publish = None
        self.on_subscribe = None
        self.on_message = None

    @abstractmethod
    def connect(self, host, port=1883, keepalive=60):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def publish(self, topic, payload, qos=0):
        pass

    @abstractmethod
    def subscribe(self, topic):
        pass

    @abstractmethod
    def unsubscribe(self, topic):
        pass

    @abstractmethod
    def loop_start(self, event_loop):
        """Starts the event loop integration."""
        pass

    @abstractmethod
    def loop_stop(self):
        """Stops the event loop integration."""
        pass

    @abstractmethod
    def username_pw_set(self, username, password=None):
        pass

    @abstractmethod
    def tls_set(
        self,
        ca_certs=None,
        certfile=None,
        keyfile=None,
        cert_reqs=None,
        tls_version=None,
        ciphers=None,
    ):
        pass

    @abstractmethod
    def tls_set_context(self, context=None):
        pass

    @abstractmethod
    def tls_insecure_set(self, value):
        pass

    @abstractmethod
    def message_callback_add(self, sub, callback):
        pass

    @abstractmethod
    def message_callback_remove(self, sub):
        pass

    @abstractmethod
    def socket(self):
        pass

    @property
    @abstractmethod
    def _out_packet(self):
        pass


class PahoMQTTTransport(Transport):
    """
    Transport implementation using Paho MQTT Client.
    """

    def __init__(self, client_id, clean_session=True):
        super().__init__()
        self.mqttc = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2, client_id, clean_session=clean_session
        )
        self.aioh = None

        # Proxy callbacks
        self.mqttc.on_connect = self._on_connect_wrapper
        self.mqttc.on_disconnect = self._on_disconnect_wrapper
        self.mqttc.on_publish = self._on_publish_wrapper
        self.mqttc.on_subscribe = self._on_subscribe_wrapper
        self.mqttc.on_message = self._on_message_wrapper

    def _on_connect_wrapper(self, client, userdata, flags, rc, properties):
        if self.on_connect:
            self.on_connect(client, userdata, flags, rc, properties)

    def _on_disconnect_wrapper(self, client, userdata, rc, properties):
        if self.on_disconnect:
            self.on_disconnect(client, userdata, rc, properties)

    def _on_publish_wrapper(self, client, userdata, mid, rc, properties):
        if self.on_publish:
            self.on_publish(client, userdata, mid, rc, properties)

    def _on_subscribe_wrapper(self, client, userdata, mid, rc_list, properties):
        if self.on_subscribe:
            self.on_subscribe(client, userdata, mid, rc_list, properties)

    def _on_message_wrapper(self, client, userdata, msg):
        if self.on_message:
            self.on_message(client, userdata, msg)

    def connect(self, host, port=1883, keepalive=60):
        return self.mqttc.connect(host, port, keepalive)

    def disconnect(self):
        self.mqttc.disconnect()

    def publish(self, topic, payload, qos=0):
        return self.mqttc.publish(topic, payload, qos)

    def subscribe(self, topic):
        return self.mqttc.subscribe(topic)

    def unsubscribe(self, topic):
        return self.mqttc.unsubscribe(topic)

    def loop_start(self, event_loop):
        self.aioh = AsyncioMQTTHelper(event_loop, self.mqttc)

    def loop_stop(self):
        # AsyncioMQTTHelper doesn't seem to have a clear stop/cleanup method exposed
        # but the event loop controls it.
        pass

    def username_pw_set(self, username, password=None):
        self.mqttc.username_pw_set(username, password)

    def tls_set(
        self,
        ca_certs=None,
        certfile=None,
        keyfile=None,
        cert_reqs=None,
        tls_version=None,
        ciphers=None,
    ):
        self.mqttc.tls_set(ca_certs, certfile, keyfile, cert_reqs, tls_version, ciphers)

    def tls_set_context(self, context=None):
        self.mqttc.tls_set_context(context)

    def tls_insecure_set(self, value):
        self.mqttc.tls_insecure_set(value)

    def message_callback_add(self, sub, callback):
        self.mqttc.message_callback_add(sub, callback)

    def message_callback_remove(self, sub):
        self.mqttc.message_callback_remove(sub)

    def socket(self):
        return self.mqttc.socket()

    @property
    def _out_packet(self):
        return self.mqttc._out_packet


class MockMQTTTransport(Transport):
    """
    Mock Transport for testing.
    """

    def __init__(self, client_id, clean_session=True):
        super().__init__()
        self.client_id = client_id
        self.connected = False
        self.subscriptions = {}  # topic -> callback
        self.published_messages = []
        self._out_packet_mock = 0

    def connect(self, host, port=1883, keepalive=60):
        self.connected = True
        # If event loop is already started, schedule the connection callback
        if hasattr(self, "event_loop") and self.event_loop:
            self._schedule_connect()
        return 0

    def disconnect(self):
        self.connected = False
        if self.on_disconnect:
            self.on_disconnect(self, None, 0, None)

    def publish(self, topic, payload, qos=0):
        self.published_messages.append({"topic": topic, "payload": payload, "qos": qos})
        if self.on_publish:
            self.on_publish(self, None, 1, 0, None)
        return None

    def subscribe(self, topic):
        # mid=1 (fixed for mock)
        mid = 1
        self.subscriptions[topic] = (
            None  # No specific callback added yet via add, just general sub
        )
        return (0, mid)  # (result, mid)

    def unsubscribe(self, topic):
        if topic in self.subscriptions:
            del self.subscriptions[topic]
        return (0, 1)

    def loop_start(self, event_loop):
        self.loop_start_called = True
        self.event_loop = event_loop
        if self.connected:
            self._schedule_connect()

    def _schedule_connect(self):
        # We need to trigger on_connect on the loop
        async def _trigger():
            await asyncio.sleep(0.01)
            if self.on_connect:
                self.on_connect(self, None, {}, 0, None)

        # We can add a task to the event_loop wrapper
        from .event_loop import AsyncWorker

        w = AsyncWorker(self.event_loop, _trigger, None)
        self.event_loop.add_task(w)

    def loop_stop(self):
        pass

    def username_pw_set(self, username, password=None):
        pass

    def tls_set(
        self,
        ca_certs=None,
        certfile=None,
        keyfile=None,
        cert_reqs=None,
        tls_version=None,
        ciphers=None,
    ):
        pass

    def tls_set_context(self, context=None):
        pass

    def tls_insecure_set(self, value):
        pass

    def message_callback_add(self, sub, callback):
        # Store callback for this subscription
        self.subscriptions[sub] = callback

    def message_callback_remove(self, sub):
        if sub in self.subscriptions:
            del self.subscriptions[sub]

    def socket(self):
        class MockSocket:
            def setsockopt(self, *args, **kwargs):
                pass

        return MockSocket()

    @property
    def _out_packet(self):
        return self._out_packet_mock

    def mock_receive(self, topic, payload):
        """Simulate receiving a message."""

        # Simple mock message object
        class MockMsg:
            def __init__(self, t, p):
                self.topic = t
                self.payload = p
                self.qos = 0
                self.retain = False

        msg = MockMsg(topic, payload)

        # Find matching subscription
        matched = False
        for sub, callback in self.subscriptions.items():
            if topic_matches_sub(sub, topic):
                if callback:
                    callback(self, None, msg)
                    matched = True

        if not matched and self.on_message:
            self.on_message(self, None, msg)


class RecorderTransport(Transport):
    """
    Wraps another Transport to record input/output messages.
    """

    def __init__(self, inner_transport, trace_file="mqtt_trace.json"):
        super().__init__()
        self.inner = inner_transport
        self.trace_file = trace_file
        self.events = []

        # Proxy properties
        self.inner.on_connect = self._on_connect_wrapper
        self.inner.on_disconnect = self._on_disconnect_wrapper
        self.inner.on_publish = self._on_publish_wrapper
        self.inner.on_subscribe = self._on_subscribe_wrapper
        self.inner.on_message = self._on_message_wrapper

    def _on_connect_wrapper(self, client, userdata, flags, rc, properties):
        if self.on_connect:
            self.on_connect(client, userdata, flags, rc, properties)

    def _on_disconnect_wrapper(self, client, userdata, rc, properties):
        if self.on_disconnect:
            self.on_disconnect(client, userdata, rc, properties)

    def _on_publish_wrapper(self, client, userdata, mid, rc, properties):
        if self.on_publish:
            self.on_publish(client, userdata, mid, rc, properties)

    def _on_subscribe_wrapper(self, client, userdata, mid, rc_list, properties):
        if self.on_subscribe:
            self.on_subscribe(client, userdata, mid, rc_list, properties)

    def _on_message_wrapper(self, client, userdata, msg):
        # Record INCOMING message
        try:
            payload = msg.payload.decode("utf-8")
            # Try parsing JSON to store structured data
            try:
                payload = json.loads(payload)
            except json.JSONDecodeError:
                pass
        except (UnicodeDecodeError, AttributeError):
            payload = str(msg.payload)

        self.events.append(
            {
                "type": "input",
                "timestamp": time.time(),
                "topic": msg.topic,
                "payload": payload,
            }
        )
        if self.on_message:
            self.on_message(client, userdata, msg)
        self.save_trace()

    def connect(self, host, port=1883, keepalive=60):
        return self.inner.connect(host, port, keepalive)

    def disconnect(self):
        self.save_trace()
        return self.inner.disconnect()

    def publish(self, topic, payload, qos=0):
        # Record OUTGOING message
        try:
            # payload can be string or bytes
            p = payload
            if isinstance(p, bytes):
                p = p.decode("utf-8")
            try:
                p = json.loads(p)
            except json.JSONDecodeError:
                pass
        except (UnicodeDecodeError, AttributeError):
            p = str(payload)

        self.events.append(
            {"type": "output", "timestamp": time.time(), "topic": topic, "payload": p}
        )
        self.save_trace()
        return self.inner.publish(topic, payload, qos)

    def subscribe(self, topic):
        return self.inner.subscribe(topic)

    def unsubscribe(self, topic):
        return self.inner.unsubscribe(topic)

    def loop_start(self, event_loop):
        self.inner.loop_start(event_loop)

    def loop_stop(self):
        self.save_trace()
        self.inner.loop_stop()

    def save_trace(self):
        try:
            with open(self.trace_file, "w") as f:
                json.dump(self.events, f, indent=2)
        except Exception as e:
            print(f"Error saving trace: {e}")

    # Forward other methods
    def username_pw_set(self, *args, **kwargs):
        self.inner.username_pw_set(*args, **kwargs)

    def tls_set(self, *args, **kwargs):
        self.inner.tls_set(*args, **kwargs)

    def tls_set_context(self, *args, **kwargs):
        self.inner.tls_set_context(*args, **kwargs)

    def tls_insecure_set(self, *args, **kwargs):
        self.inner.tls_insecure_set(*args, **kwargs)

    def message_callback_add(self, sub, callback):
        self.inner.message_callback_add(sub, callback)

    def message_callback_remove(self, sub):
        self.inner.message_callback_remove(sub)

    def socket(self):
        return self.inner.socket()

    @property
    def _out_packet(self):
        return self.inner._out_packet
