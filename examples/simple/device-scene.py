"""Device Scene

Demonstrate starting two connections, for a scene and a device, and communicating between them.
"""

import json
import random
from datetime import datetime

from arena import Box, Device, Material, Scene

box = Box(object_id="box", position=(0, 2, -1), rotation=(0, 0, 0),
          scale=(2, 2, 2), material=Material(transparent=True, opacity=1))

scene = Scene(host="arenaxr.org", scene="example")
device = Device(host="arenaxr.org", device="robot1")

CUSTOM_TOPIC = f"{device.realm}/d/{device.namespace}/{device.device}/rtc1"


def on_recv_message_device(client, userdata, msg):
    try:
        payload_str = msg.payload.decode("utf-8", "ignore")
        payload = json.loads(payload_str)
        print(payload)

        box.data.position.x += 1
        box.data.rotation.x += 0.1
        box.data.scale.y -= 0.01
        box.data.material.opacity = (box.data.material.opacity - 0.01) % 1
        print(scene.update_object(
            box,
            click_listener=True,
        ))
    except:
        pass


device.message_callback_add(CUSTOM_TOPIC, on_recv_message_device)


@device.run_forever(interval_ms=1000)
def on_second_publ_message():
    payload = {}
    d = datetime.now().isoformat()[:-3]+"Z"
    payload["timestamp"] = d
    payload = json.dumps(payload)
    device.publish(CUSTOM_TOPIC, payload)


device.run_tasks()
