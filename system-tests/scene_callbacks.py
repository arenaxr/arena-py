# scene_callbacks.py
#
# Tests scene callbacks

from arena import *

def new_obj_callback(scene, obj, msg):
    print("new", obj, obj.data.position)

def on_msg_callback(scene, obj, msg):
    print("msg", obj, obj.data.position)

def delete_obj_callback(scene, obj, msg):
    print("delete", obj, obj.object_id)

scene = Scene(
              host="arena.andrew.cmu.edu", realm="realm", scene="test",
              new_obj_callback=new_obj_callback,
              on_msg_callback=on_msg_callback,
              delete_obj_callback=delete_obj_callback
            )

scene.run_tasks()
