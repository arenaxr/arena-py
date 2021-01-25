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
arena = Arena(host="arena.andrew.cmu.edu", realm="realm", scene="example", on_msg_callback=objects_callback)

@arena.run_async
async def test():
    # subscribe to secondary (in this case the network graph!)
    arena.add_topic(TOPIC, secondary_callback)
    print(f"Subscribed to {TOPIC}")
    print()

    # sleep for 5 seconds
    await arena.sleep(5000)

    # unsubscribe to secondary
    arena.remove_topic(TOPIC)
    print()
    print(f"Unsubscribed to {TOPIC}")
    print()

# our main event loop
arena.run_tasks()
