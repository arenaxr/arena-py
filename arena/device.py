import json
import os
import re
import sys

from .arena_mqtt import ArenaMQTT


class Device(ArenaMQTT):
    """
    Gives access to an ARENA device.
    Can create and execute various user-defined functions/tasks.

    :param str host: Hostname of the MQTT broker (required).
    :param str realm: Reserved topic fork for future use (optional).
    :param str namespace: Username of authenticated user or other namespace (automatic).
    :param str device: The name of the device, without namespace (required).
    """

    def __init__(
                self,
                realm = "realm",
                network_latency_interval = 10000,  # run network latency update every 10s
                on_msg_callback = None,
                end_program_callback = None,
                debug = False,
                **kwargs
            ):
        if os.environ.get("DEVICE"):
            self.device = os.environ["DEVICE"]
        elif "device" in kwargs and kwargs["device"]:
            if re.search("/", kwargs["device"]):
                sys.exit("device argument (device) cannot include '/', aborting...")
            self.device = kwargs["device"]
            print("Cannot find DEVICE environmental variable, using input parameter instead.")
        else:
            sys.exit("device argument (device) is unspecified or None, aborting...")
        super().__init__(
            realm,
            network_latency_interval,
            on_msg_callback,
            end_program_callback,
            debug,
            **kwargs
        )
        print(f"Device topic ready: {self.realm}/d/{self.namespace}/{self.device}, host={self.host}")

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
                return

    def publish(self, topic, payload_obj):
        """Publishes to mqtt broker."""
        payload = json.dumps(payload_obj)
        self.mqttc.publish(topic, payload, qos=0)
        if self.debug: print("[publish]", topic, payload)
        return payload
