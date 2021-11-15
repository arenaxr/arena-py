import json
from datetime import datetime

from arena import Device

device = Device(host="arenaxr.org", device="robot1", debug=True)
CUSTOM_TOPIC = f"{device.realm}/d/{device.namespace}/{device.device}/rtc1"


def on_recv_message(client, userdata, msg):
    try:
        payload_str = msg.payload.decode("utf-8", "ignore")
        payload = json.loads(payload_str)
        print(payload)
    except:
        pass


device.message_callback_add(CUSTOM_TOPIC, on_recv_message)


@device.run_forever(interval_ms=1000)
def on_second_publ_message():
    payload = {}
    d = datetime.now().isoformat()[:-3]+"Z"
    payload["timestamp"] = d
    payload = json.dumps(payload)
    device._publish(CUSTOM_TOPIC, payload)


device.run_tasks()
