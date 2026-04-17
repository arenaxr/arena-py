import json
import os
import re
import sys

from .arena_mqtt import ArenaMQTT
from .delta import deep_diff
from .env import DEVICE, _get_env


class Device(ArenaMQTT):
    """
    Gives access to an ARENA device.
    Can create and execute various user-defined functions/tasks.

    :param str host: Hostname of the ARENA webserver (required).
    :param str realm: Reserved topic fork for future use (optional).
    :param str namespace: Username of authenticated user or other namespace (automatic).
    :param str device: The name of the device, without namespace (required).
    :param int network_latency_interval: Interval (in ms) to run network graph latency update. Default value is 10000 (10 secs). Ignore this parameter (optional).
    :param func on_msg_callback: Called on all MQTT messages received (optional).
    :param func end_program_callback: Called on MQTT disconnect (optional).
    :param bool debug: If true, print a log of all publish messages from this client (optional).
    """

    def __init__(
        self,
        host="arenaxr.org",
        realm="realm",
        network_latency_interval=10000,  # run network latency update every 10s
        on_msg_callback=None,
        end_program_callback=None,
        debug=False,
        delta_compression=True,
        **kwargs,
    ):

        if os.environ.get(DEVICE):
            self.device = _get_env(DEVICE)
            print(f"Using Device from 'DEVICE' env variable: {self.device}")
        elif "device" in kwargs and kwargs["device"]:
            if re.search("/", kwargs["device"]):
                sys.exit("Device argument (device) cannot include '/', aborting...")
            self.device = kwargs["device"]
            print(f"Using Device from 'device' input parameter: {self.device}")
        else:
            sys.exit("Device argument (device) is unspecified or None, aborting...")

        super().__init__(host, realm, network_latency_interval, on_msg_callback, end_program_callback, debug, **kwargs)
        print(f"Device topic ready: {self.realm}/d/{self.namespace}/{self.device}, mqtt_host={self.mqtt_host}")

        # Delta compression: shadow map of last-published data dicts
        self.delta_compression = delta_compression
        self._last_published_state = {}  # object_id -> data dict

    async def process_message(self):
        while True:
            msg = await self.msg_queue.get()
            # extract payload
            try:
                payload_str = msg.payload.decode("utf-8", "ignore")
                payload = json.loads(payload_str)
            except Exception as e:
                print("Malformed payload, ignoring:")
                print(e)
                continue

    def publish(self, topic, payload_obj):
        """Publishes to mqtt broker."""
        # Apply delta compression if enabled
        if self.delta_compression:
            object_id = payload_obj.get("object_id")
            action = payload_obj.get("action")
            data = payload_obj.get("data")

            if object_id and data is not None:
                if action == "delete":
                    self._last_published_state.pop(object_id, None)
                elif action == "create" or object_id not in self._last_published_state:
                    import copy
                    self._last_published_state[object_id] = copy.deepcopy(data)
                elif action == "update":
                    import copy
                    prev_data = self._last_published_state[object_id]
                    delta = deep_diff(prev_data, data)
                    self._last_published_state[object_id] = copy.deepcopy(data)
                    payload_obj = {**payload_obj, "data": delta}

        payload = json.dumps(payload_obj)
        self.transport.publish(topic, payload, qos=0)
        if self.debug:
            print(f"[publish] {topic} {payload}")
        return payload

    def on_publish(self, client, userdata, mid, rc, properties):
        pass
