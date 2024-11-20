""" socket-server.py
    Accept incoming socket json and publish to ARENA.  An example of using non-blocking threads to
    allow ARENA-enabled applications to execute infinite `while True` loops.

    !!!!!!!
    WARNING: This example subverts ARENA MQTT security by adding a new socket server layer you must
             secure yourself.
    !!!!!!!
"""
import json
import socket
import threading
import time

from arena import *

SOCK_SERVER_HOST = "localhost"
SOCK_SERVER_PORT = 8888
SOCK_THREAD_NAME = "unsecured publisher"

scene = Scene(host="arenaxr.org", scene="test")
print("opened secured mqtt socket.")


def background_task():
    print("opening unsecured generic socket...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((SOCK_SERVER_HOST, SOCK_SERVER_PORT))
    sock.listen(1)  # num. allowed concurrent connects, socket.SOMAXCONN = 128 on some systems

    while True:
        conn, _ = sock.accept()
        data = conn.recv(1024)
        conn.close()
        publish_unauthenticated_json(data)
        # block a bit
        time.sleep(0.01)


def publish_unauthenticated_json(data):
    print(f"received unauthenticated {data}")
    payload = json.loads(data)
    payload["action"] = "update"
    topic = PUBLISH_TOPICS.SCENE_OBJECTS.substitute({**scene.topicParams, **{"objectId": payload['object_id']}})
    print("publishing on secured mqtt socket...")
    scene.mqttc.publish(topic, json.dumps(payload), qos=0)


@scene.run_once
def load_thread():
    # create and start the daemon thread
    print("starting background task...")
    daemon = threading.Thread(target=background_task, daemon=True, name=SOCK_THREAD_NAME)
    daemon.start()
    print("main thread is free.")


scene.run_tasks()
