import json
import signal
import sys
import time

import paho.mqtt.client as mqtt

mqtt_broker = "oz.andrew.cmu.edu"
scene_path = "realm/s/render/"
object_name = "sphere_y"

# Object starting point, global so click handler can modify it
x = 5.0
y = 5.0
z = 1.0
chaser = False


def signal_handler(sig, frame):
    client.publish(
        scene_path + object_name,
        '{"object_id": "' + object_name + '", "action": "delete"}',
        retain=True,
    )
    print("Removing objects before I quit...")
    time.sleep(1)
    sys.exit(0)


# define callbacks
def on_click_input(client, userdata, msg):
    global x
    global y
    global z
    global chaser
    jsonMsg = json.loads(msg.payload)
    if jsonMsg["action"] != "clientEvent":
        return
    if jsonMsg["type"] != "mousedown":
        return
    print('got click: %s "%s"' % (msg.topic, msg.payload))
    click_x = jsonMsg["data"]["position"]["x"]
    click_y = jsonMsg["data"]["position"]["y"]
    click_z = jsonMsg["data"]["position"]["z"]
    user = jsonMsg["data"]["source"]
    print(user)
    print("Clicked by: " + user)
    obj_x = float(x) - float(click_x)
    obj_y = float(y) - float(click_y)
    obj_z = float(z) - float(click_z)
    if jsonMsg["type"] == "mousedown" and chaser == False:
        print("Obj relative click: " + str(obj_x) + "," + str(obj_y) + "," + str(obj_z))
        client.subscribe(scene_path + user)
        client.message_callback_add(scene_path + user, on_camera)
        chaser = True
        color = "#00FF00"
        # sphere_str = object_name + ",{},{},{},0,0,0,0,1,1,1,{},on"
        MESSAGE = {
            "object_id": object_name,
            "action": "create",
            "data": {
                "object_type": "sphere",
                "position": {"x": x, "y": y, "z": z},
                "color": color,
            },
        }

        client.publish(scene_path + object_name, json.dumps(MESSAGE), retain=False)
    else:
        client.unsubscribe(scene_path + user)
        print("Unsubscribing from camera")
        chaser = False
        color = "#FF0000"
        # sphere_str = object_name + ",{},{},{},0,0,0,0,1,1,1,{},on"
        MESSAGE = {
            "object_id": object_name,
            "action": "create",
            "data": {
                "object_type": "sphere",
                "position": {"x": x, "y": y, "z": z},
                "color": color,
            },
        }
        client.publish(scene_path + object_name, json.dumps(MESSAGE), retain=False)


# /topic/render/camera_7452_X camera_7452_X,-9.979,1.600,-2.760,-0.062,-0.855,-0.105,0.504,0,0,0,#8e1191,on
def on_camera(client, userdata, msg):
    global x
    global y
    global z
    print("got camera: %s '%s'" % (msg.topic, msg.payload))
    jsonMsg = json.loads(msg.payload)
    # t,cam_x,cam_y,cam_z, t, t, t, t, t, t, t, t, t, t = msg.payload.split(',')
    cam_x = jsonMsg["data"]["position"]["x"]
    cam_y = jsonMsg["data"]["position"]["y"]
    cam_z = jsonMsg["data"]["position"]["z"]
    print(cam_x, cam_y, cam_z)
    x = str(float(cam_x) + 3.0)
    y = cam_y
    z = cam_z


client = mqtt.Client("client-002", clean_session=True, userdata=None)

print("connecting to broker ", mqtt_broker)
client.connect(mqtt_broker)

client.subscribe(scene_path + object_name)
client.message_callback_add(scene_path + object_name, on_click_input)

############
# Setup box
# Delete the object from the scene to get a fresh start with a null message
client.publish(
    scene_path + object_name,
    '{"object_id": "' + object_name + '", "action": "delete"}',
    retain=True,
)
# color = "#%06x" % random.randint(0, 0xFFFFFF)
color = "#FF0000"
# sphere_str = object_name + ",{},{},{},0,0,0,0,1,1,1,{},on"
# sphere_str.format(x,y,z,color)
MESSAGE = {
    "object_id": object_name,
    "action": "create",
    "data": {
        "object_type": "sphere",
        "position": {"x": x, "y": y, "z": z},
        "color": color,
    },
}
# Publish a sphere with x,y,z and color parameters
# retain=True makes it persistent
client.publish(scene_path + object_name, json.dumps(MESSAGE), retain=False)

# Enable click listener for object (allows it to be clickable)
MESSAGE = {
    "object_id": object_name,
    "action": "update",
    "type": "object",
    "data": {"click-listener": "enable"},
}
client.publish(scene_path + object_name, json.dumps(MESSAGE), retain=False)

client.loop_start()  # start loop to process received mqtt messages
# add signal handler to remove objects on quit
signal.signal(signal.SIGINT, signal_handler)

# Main loop that runs every 5 seconds and changes the object color
while True:
    print("Main chaser loop")
    # sphere_str = "property: position; to: {} {} {}; dur: 1000; easing: linear"
    # Publish an animation command to move the object sphere_str.format(x,y,z)
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
    client.publish(scene_path + object_name, json.dumps(MESSAGE), retain=False)
    time.sleep(1.0)

client.disconnect()  # disconnect
client.loop_stop()  # stop loop
