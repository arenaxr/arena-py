# camera-child.py
''' Demonstrate setting an object to be a child of a camera
'''
from arena import *

scene = Scene(host="arenaxr.org", realm="realm", scene="example")

def user_join_callback(scene, cam, msg):
    if "camera" in cam.object_id:
        circle1 = Circle(
            parent=cam.object_id,
            position=(-.5, 0, -.5),
            scale=(0.05, 0.05, 0.05)
        )
        circle2 = Circle(
            parent=cam.object_id,
            position=(.5, 0, -.5),
            scale=(0.05, 0.05, 0.05),
            ttl=5
        )
        scene.add_object(circle1)
        scene.add_object(circle2)

scene.user_join_callback = user_join_callback

print("Go to URL: https://arenaxr.org/example")

# our main event loop
scene.run_tasks()
