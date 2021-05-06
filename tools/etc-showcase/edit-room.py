from arena import *
import time

# setup library
scene = Scene(host="arenaxr.org", realm="realm", scene="test")

def edit_scene_options():
    # create generic object for scene-options
    opt_obj = Object(object_id='scene-options', persist=True)
    opt_obj.type = 'scene-options'
    del opt_obj.data.object_type

    # scene options we want to edit (comment-out to leave the persisted value unchanged)
    opt_obj.data['scene-options'] = {
        #"clickableOnlyEvents": True,
        #"privateScene": True,
        "jitsiHost": "mr.andrew.cmu.edu",
        #"maxAVDist": 20,
        #"screenshare": "screenshare",
        #"volume": 1,
        #"distanceModel": "inverse",
        #"refDistance": 1,
        #"rolloffFactor": 1
    }
    scene.update_object(opt_obj)

def add_program():
    # create generic object for program
    program_obj = Object(persist=True)
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

@scene.run_once
def run_all():
    edit_scene_options()
    add_program()
    time.sleep(2) # give time to publish messages
    print("Done!")

    scene.task_manager.shutdown_wrapper()

# start tasks
scene.run_tasks()
