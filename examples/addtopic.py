# addtopic.py
''' Demonstrate subscribing to a secondary topic on the same broker and monitor
messages from the secondary topic within the same program.
'''

from arena import *
import json

TOPIC = "$NETWORK"

def objects_callback(scene, obj, msg):
    print("Object message: "+str(msg))


def secondary_callback(scene, obj, msg):
    print("-----")
    print(f"Secondary message:\nTopic: {str(msg.topic)}\nPayload: {json.loads(msg.payload)}")
    print("-----")


# subscribe to objects
scene = Scene(host="mqtt.arenaxr.org", scene="example", on_msg_callback=objects_callback)

@scene.run_async
async def test():
    # subscribe to secondary (in this case the network graph!)
    scene.message_callback_add(TOPIC, secondary_callback)
    print(f"Subscribed to {TOPIC}")
    print()

    # sleep for 5 seconds
    await scene.sleep(5000)

    # unsubscribe to secondary
    scene.message_callback_remove(TOPIC)
    print()
    print(f"Unsubscribed to {TOPIC}")
    print()

# our main event loop
scene.run_tasks()
