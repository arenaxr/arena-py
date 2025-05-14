import time
import uuid

from arena import *

# setup library
scene = Scene(host="arenaxr.org", namespace="etc", scene="ProjectHub_2")

def edit_scene_options():
    # create generic object for scene-options
    opt_obj = Object(object_id='scene-options', persist=True)
    opt_obj.type = 'scene-options'
    del opt_obj.data.object_type

    # scene options we want to edit (comment-out to leave the persisted value unchanged)
    opt_obj.data['scene-options'] = {
        #"clickableOnlyEvents": True,
        #"privateScene": True,
        "jitsiHost": "mr.lan.cmu.edu",
        #"maxAVDist": 20,
        #"screenshare": "screenshare",
        #"volume": 1,
        #"distanceModel": "inverse",
        #"refDistance": 1,
        #"rolloffFactor": 1
    }
    scene.update_object(opt_obj)

def add_program():
    # create a uuid based on the scene name
    obj_uuid = uuid.uuid5(uuid.UUID('000102030405060708090a0b0c0d0e0f'), str(scene.scene))

    # create generic object for program
    program_obj = Object(object_id=str(obj_uuid), persist=True)
    program_obj.type = 'program'
    del program_obj.data.object_type

    # program data
    program_obj.data['name'] = 'arena/py/etc-showcase'
    program_obj.data['instantiate'] = 'single'
    program_obj.data['filename'] = 'etc-room.py'
    program_obj.data['filetype'] = 'PY'
    program_obj.data['env'] = [
          "MID=${moduleid}",
          "SCENE=${scene}",
          "NAMESPACE=${namespace}",
          "MQTTH=${mqtth}",
          "REALM=realm"]
    scene.add_object(program_obj)

def edit_teleporter_project_rooms():
    teleporter_obj = scene.get_persisted_obj('[Teleporter]')
    if not teleporter_obj: return

    # change goto-url target
    teleporter_obj.data['goto_url']['url']='https://arenaxr.org/etc/ProjectHub?skipav=true&startLastPos=true'

    scene.update_object(teleporter_obj)

def edit_teleporter_hub_world():
    scene_objs = scene.get_persisted_objs()

    for obj_id,obj in scene_objs.items():
        if obj['type'] == 'object':
            update=False
            if hasattr(obj['data'], 'goto_url'):
                if obj['data']['goto_url']['url'].endswith('?skipav=True'):
                    new_url = obj['data']['goto_url']['url'].replace('?skipav=True', '')
                    obj['data']['goto_url']['url'] = new_url
                    update=True

            if update:
                scene.update_object(obj)

def edit_assets():
    scene_objs = scene.get_persisted_objs()

    for obj_id,obj in scene_objs.items():
        if obj['type'] == 'object':
            update=False
            if hasattr(obj['data'], 'url'):
                if obj['data']['url'].startswith('/store/users/'):
                    obj['data']['url'] = f"https://arena-cdn.conix.io{obj['data']['url']}"
                    print(obj['data']['url'])
                    update=True
                if obj['data']['url'].startswith('store/users/'):
                    obj['data']['url'] = f"https://arena-cdn.conix.io/{obj['data']['url']}"
                    print(obj['data']['url'])
                    update=True
            if hasattr(obj['data'], 'material'):
                if hasattr(obj['data']['material'], 'src'):
                    if obj['data']['material']['src'].startswith('/store/users/'):
                        obj['data']['material']['src'] = f"https://arena-cdn.conix.io{obj['data']['material']['src']}"
                        update=True
                    if obj['data']['material']['src'].startswith('store/users/'):
                        obj['data']['material']['src'] = f"https://arena-cdn.conix.io/{obj['data']['material']['src']}"
                        update=True
                    update=True

            if update:
                scene.update_object(obj)

@scene.run_once
def run_all():
    #edit_scene_options()
    #add_program()
    edit_teleporter_project_rooms()
    #edit_teleporter_hub_world()
    #edit_assets()
    #time.sleep(2) # give time to publish messages
    #print("Done!")

    scene.task_manager.shutdown_wrapper()

# start tasks
scene.run_tasks()
