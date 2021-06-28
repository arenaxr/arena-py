from arena import *

scene = Scene(host="arenaxr.org", scene="example")

CUSTOM_TOPIC = "$NETWORK"

def on_msg_callback(client, userdata, msg):
    try:
        payload_str = msg.payload.decode("utf-8", "ignore")
        payload  = json.loads(payload_str)
        print(payload)
    except:
        pass

scene.message_callback_add(CUSTOM_TOPIC, on_msg_callback)

scene.run_tasks()
