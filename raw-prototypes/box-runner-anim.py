import json
import random
import time

import numpy
import paho.mqtt.client as paho

broker = "oz.andrew.cmu.edu"
object_name = "cube_x"
object_path = "realm/s/render/"


# define callback
def on_message(client, userdata, message):
    time.sleep(1)
    print("received message =", str(message.payload.decode("utf-8")))


client = paho.Client("client-001")

######Bind function to callback
client.on_message = on_message
#####
print("connecting to broker ", broker)
client.connect(broker)
# connect
client.loop_start()  # start loop to process received messages
# client.subscribe("house/bulb1")#subscribe
print("publishing intial box")
MESSAGE = {
    "object_id": "cube_2",
    "action": "create",
    "data": {"object_type": "cube", "color": "#AA0000"},
}
client.publish("realm/s/cube_2", json.dumps(MESSAGE))

# client.publish(object_path+object_name+"/animation","property: position; to: 5 1.6 0; dur: 1500; easing: linear")
while True:
    x = 1.0
    y = 1.0
    z = 1.0
    color = "#%06x" % random.randint(0, 0xFFFFFF)
    # cube_str = object_name + ",{},{},{},0,0,0,0,1,1,1,{},on"
    # client.publish(object_path+object_name,cube_str.format(x,y,z,color))
    MESSAGE = {
        "object_id": object_name,
        "action": "create",
        "data": {
            "object_type": "cube",
            "position": {"x": x, "y": y, "z": z},
            "color": color,
        },
    }
    client.publish(object_path + object_name, json.dumps(MESSAGE))

    # cube_str = "property: position; to: {} {} {}; dur: 1000; easing: linear"

    # Walk out
    for x in numpy.arange(0.0, 20.0, 1.0):
        y = 1
        z += random.random()
        MESSAGE = {
            "object_id": object_name,
            "action": "update",
            "type": "object",
            "data": {
                "animation": {
                    "property": "position",
                    "to": str(x) + " " + str(y) + " " + str(z),
                    "easing": "linear",
                    "dur": 1000,
                }
            },
        }
        client.publish(object_path + object_name, json.dumps(MESSAGE))

        #    client.publish(object_path+object_name,cube_str.format(x,y,z,color))
        time.sleep(1.0)

    # Walk back
    for x in numpy.arange(20.0, 0.0, -1.0):
        y = 1
        z -= random.random()
        MESSAGE = {
            "object_id": object_name,
            "action": "update",
            "type": "object",
            "data": {
                "animation": {
                    "property": "position",
                    "to": str(x) + " " + str(y) + " " + str(z),
                    "easing": "linear",
                    "dur": 1000,
                }
            },
        }
        client.publish(object_path + object_name, json.dumps(MESSAGE))
        #    client.publish(object_path+object_name,cube_str.format(x,y,z,color))
        time.sleep(1.0)

client.disconnect()  # disconnect
client.loop_stop()  # stop loop
