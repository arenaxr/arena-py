import json
import urllib.request

import paho.mqtt.client as mqtt


def get_token(scene, user):
    url = 'https://xr.andrew.cmu.edu:8888/?scene='+scene+'&username='+user
    return urllib.request.urlopen(url).read()


def on_connect(client, userdata, flags, rc):
    # The callback for when the client receives a CONNACK response from the server.
    # print(client.__dict__)
    # print(userdata)
    # print(flags)
    # print(rc)

    if rc == 0:
        print("connected")
    else:
        print("connection refused, result code: "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("realm/s/auth-test/#")

    client.publish("realm/s/auth-test", "TEST MESSAGE from python  ")


def on_message(client, userdata, msg):
    # The callback for when a PUBLISH message is received from the server.
    # print(client.__dict__)
    # print(userdata)
    # print(msg.__dict__)

    print(msg.topic+" "+str(msg.payload))


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

user = "editor"
tokeninfo = json.loads(get_token("auth-test", "editor").decode('utf-8'))
token = tokeninfo['token']
print('user: '+user+', token: '+token)
client.username_pw_set(username=user, password=token)

client.connect("oz.andrew.cmu.edu", 1884)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
