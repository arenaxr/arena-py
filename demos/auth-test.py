import json
import urllib.request

import paho.mqtt.client as mqtt


def get_token(scene, user):
    url = 'https://xr.andrew.cmu.edu:8888/?scene='+scene+'&username='+user
    return urllib.request.urlopen(url).read()


def on_connect(client, userdata, flags, rc):
    print("on_connect")
    print(userdata)
    print(flags)
    print(rc)

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("realm/s/auth-test/#")

    msg = '{"object_id" : "cube_1", "action": "create", "type": "object", "data": {"object_type": "cube", "position": {"x": 1, "y": 1, "z": -1}, "rotation": {"x": 0, "y": 0, "z": 0, "w": 1}, "scale": {"x": 1, "y": 1, "z": 1}, "color": "#FF0000"}}'
    client.publish("realm/s/auth-test/cube_1", msg)


def on_subscribe(client, userdata, mid, granted_qos):
    print("on_subscribe")
    print(userdata)
    print(mid)
    print(granted_qos)


def on_unsubscribe(client, userdata, mid):
    print("on_unsubscribe")
    print(userdata)
    print(mid)


def on_publish(client, userdata, mid):
    print("on_publish")
    print(userdata)
    print(mid)


def on_message(client, userdata, msg):
    print("on_message")
    print(userdata)
    print(msg.topic)
    print(str(msg.payload))


def on_disconnect(client, userdata, rc):
    print("on_disconnect")
    print(userdata)
    print(rc)


client = mqtt.Client()
client.on_connect = on_connect
client.on_subscribe = on_subscribe
client.on_unsubscribe = on_unsubscribe
client.on_publish = on_publish
client.on_message = on_message
client.on_disconnect = on_disconnect

user = "editor"
scene = "auth-test"
tokeninfo = json.loads(get_token(scene, user).decode('utf-8'))
token = tokeninfo['token']
print('user: '+user+', token: '+token)
client.username_pw_set(username=user, password=token)

client.connect("oz.andrew.cmu.edu", 1884)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
