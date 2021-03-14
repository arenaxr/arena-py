# addtopic.py
''' Demonstrate subscribing to a secondary topic on the same broker and monitor
messages from the secondary topic within the same program.
'''

from arena import *
import json

TOPIC = "$NETWORK"

def objects_callback(event):
    print("Object message: "+str(event))


def secondary_callback(msg):
    print("-----")
    print(f"Secondary message:\nTopic: {str(msg.topic)}\nPayload: {json.loads(msg.payload)}")
    print("-----")


# subscribe to objects
scene = Scene(host="arena.andrew.cmu.edu", realm="realm", scene="example", on_msg_callback=objects_callback)

@scene.run_async
async def test():
    # subscribe to secondary (in this case the network graph!)
    scene.add_topic(TOPIC, secondary_callback)
    print(f"Subscribed to {TOPIC}")
    print()

    # sleep for 5 seconds
    await scene.sleep(5000)

    # unsubscribe to secondary
    scene.remove_topic(TOPIC)
    print()
    print(f"Unsubscribed to {TOPIC}")
    print()

# our main event loop
scene.run_tasks()
