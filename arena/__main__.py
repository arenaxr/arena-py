"""
ARENA-py CLI

Usage: python3 -m arena -s <scene> -a <pub/sub> ...
"""

import argparse
from arena import *

# define defaults
DEFAULT_MQTT_HOST = "arenaxr.org"
PUBLISH = "pub"
SUBSCRIBE = "sub"

def on_msg_callback(scene, obj, msg):
    print(f"<{scene.root_topic}> \"{msg}\"")

def on_custom_topic_callback(client, userdata, msg):
    try:
        payload_str = msg.payload.decode("utf-8", "ignore")
        print(f"<{msg.topic}> \"{payload_str}\"")
    except:
        pass

def send_msg(scene, topic, msg):
    if topic is None:
        print(f"Publishing to topic: <{scene.root_topic}>... ", end="")
        scene.mqttc.publish(scene.root_topic, msg)
    else:
        print(f"Publishing to topic: <{topic}>... ", end="")
        scene.mqttc.publish(topic, msg)
    print("done!")

    scene.stop_tasks()


def main(mqtth, realm, scene, namespace, action, topic, message):
    scene = Scene(host=mqtth, realm=realm, scene=scene, namespace=namespace)

    if action == SUBSCRIBE:
        if topic is None:
            scene.on_msg_callback = on_msg_callback
        else:
            print(f"Subscribing to topic: <{topic}>... ", end="")
            scene.message_callback_add(topic, on_custom_topic_callback)
            print("done!")

    elif action == PUBLISH:
        if message is None:
            print("Message not specified! Aborting...")
            return
        scene.run_once(send_msg, scene=scene, topic=topic, msg=message)

    scene.run_tasks()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=("ARENA-py CLI"))

    parser.add_argument("-mh", "--mqtth",
                        type=str,
                        help="MQTT host to connect to",
                        default=DEFAULT_MQTT_HOST)
    parser.add_argument("-r", "--realm",
                        type=str,
                        help="Realm to listen to",
                        default="realm")
    parser.add_argument("-s", "--scene",
                        type=str,
                        help="Scene to listen to",
                        default="none")
    parser.add_argument("-n", "--namespace",
                        type=str,
                        help="Namespace of scene",
                        default=None)

    parser.add_argument("-a", "--action",
                        help=f"Action to do ({PUBLISH} or {SUBSCRIBE})",
                        choices=(PUBLISH, SUBSCRIBE),
                        required=True)

    parser.add_argument("-t", "--topic",
                        type=str,
                        help=f"Custom topic to publish/subscribe to")
    parser.add_argument("-m", "--message",
                        type=str,
                        help=f"Message to send (ignored when action={SUBSCRIBE})")

    args = parser.parse_args()

    main(**vars(args))
