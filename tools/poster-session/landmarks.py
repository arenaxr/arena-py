"""
*TL;DR
"""
import json
import paho.mqtt.publish as publish
from pathlib import Path

class Landmarks(dict):
    """

    Attributes
    ----------

    """

    def __init__(self, obj_id='scene-landmarks'):
        # arena landmarks object properties
        self['object_id'] = obj_id
        self['action'] = 'create'
        self['persist'] = True
        self['type'] = 'landmarks'
        self['data'] = { 'landmarks' : [] }

    def push(self, obj_id, lbl):
        self['data']['landmarks'].append({
            "object_id": obj_id,
            "label": lbl
        })

    def add_to_arena(self, scene, realm='realm', mqtt_host="arena.andrew.cmu.edu", mqtt_port=8883):
        # get mqtt credentials
        _user_mqtt_path = f'{str(Path.home())}/.arena_mqtt_auth'
        with open(_user_mqtt_path) as f:
            mqtt_auth_data = json.load(f)

        mqtt_auth = { 'username': mqtt_auth_data['username'], 'password': mqtt_auth_data['token'] }

        topic = f'{realm}/s/{mqtt_auth_data["username"]}/{scene}'
        publish.single( topic, json.dumps(self), hostname=mqtt_host, port=mqtt_port, auth=mqtt_auth)
