"""
*TL;DR
Publish objects
"""
import paho.mqtt.client as mqtt
import random
from arena import auth
import json
import time

class ARENAObjectImport():
    """

    Attributes
    ----------

    """

    def __init__(self, realm='realm', mqtt_host='arena.andrew.cmu.edu', mqtt_port=8883):
        self.realm = realm;
        debug=False
        username = auth.authenticate_user(mqtt_host, debug)
        password = None
        data = auth.authenticate_scene(
                mqtt_host, realm,
                None, username,
                debug
        )
        if 'username' in data and 'token' in data:
            username = data["username"]
            password = data["token"]

        if username is None or password is None:
            raise Exception('Failure getting credentials.')

        self.mqttc_id = "pyClient-" + str(random.randrange(100000, 999999))

        self.mqttc = mqtt.Client(self.mqttc_id, clean_session=True)
        self.mqttc.username_pw_set(username=username, password=password)
        self.mqttc.connect(mqtt_host, mqtt_port)

    def add(self, json_obj, persist=True, debug=False):
        """
        receives json_obj in the format:
        {
            "_id": { ... },
            "attributes": {
                "object_type": "arena-object-type",
                ...
            },
            "namespace": "arena-namespace",
            "object_id": "arena-object-id",
            "realm": "arena-realm",
            "sceneId": "arena-scene-name",
            "type": "arena-message-type"
        }

        persist=False for a dry run
        """
        namespace = json_obj['namespace'];
        scene = json_obj['sceneId'];
        ns_scene = f'{namespace}/{scene}'
        topic = f'{self.realm}/s/{ns_scene}'
        arena_obj = {
            'object_id': json_obj['object_id'],
            'action': 'create',
            'persist': persist,
            'type': json_obj['type'],
            'data': json_obj['attributes']
        }
        if debug: print('publishing:', topic, json.dumps(arena_obj, indent=4, sort_keys=True))
        minfo = self.mqttc.publish(topic, json.dumps(arena_obj))
        while not minfo.is_published():
            self.mqttc.loop(1)
        #infot.wait_for_publish()
        if minfo.rc != mqtt.MQTT_ERR_SUCCESS:
            raise Exception('Error publishing.')
