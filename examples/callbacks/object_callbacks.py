"""Object Callbacks

`scene.new_obj_callback` is called whenever there is a new object that has been created in the scene,
one that the user does not have a reference to. Use this to make references to any
new objects that may appear during a programs lifetime. Also a good way to find camera ID's.

`scene.delete_obj_callback` is called whenever there is an object has been deleted in the scene.
arena-py will look for all "action" = "delete" messages and call this callback.
Use this to delete references and to be notified when an object is removed by
another user or program.
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")


# [scene] is the Scene that called the callback
# [obj] will be an Object instance
# [msg] is the raw JSON message as a dict
def new_obj_callback(scene, obj, msg):
    # do stuff with obj here
    print("new", obj, obj.object_id, obj.data.position.x)
    # etc.
    # could also do obj["object_id"] or msg["object_id"]


scene.new_obj_callback = new_obj_callback


# [scene] is the Scene that called the callback
# [obj] will be an Object instance
# [msg] is the raw JSON message as a dict
def delete_obj_callback(scene, obj, msg):
    # do stuff with obj here
    print("delete", obj, obj.object_id, obj.data.position.x)
    # etc.
    # could also do obj["object_id"] or msg["object_id"]


scene.delete_obj_callback = delete_obj_callback
