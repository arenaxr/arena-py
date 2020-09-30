# addtopic.py
''' Demonstrate subscribing to a secondary topic on the same broker and monitor 
messages from the secondary topic within the same program.
'''

import arena


def objects_callback(event):
    print("Object message: "+str(event))


def secondary_callback(msg):
    print("Secondary message: "+str(msg.topic)+" "+str(msg.payload))


# subscribe to objects
arena.init("arena.andrew.cmu.edu", "realm", "hello", objects_callback)
# publish object message
arena.Object(objType=arena.Shape.sphere,
             location=(1, 1, -1), color=(255, 0, 0))
# subscribe to secondary
arena.add_topic("$SYS/#", secondary_callback)

# unsubscribe to secondary
arena.remove_topic("$SYS/#")

# our main event loop
arena.handle_events()
