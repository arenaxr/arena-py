# camera-child.py
''' Demonstrate setting an object to be a child of a camera
'''
from arena import Arena, Circle

scene = Scene(host="arena.andrew.cmu.edu", realm="realm", scene="example")

def new_obj_callback(msg):
    if "camera" in msg["object_id"]:
        circle1 = Circle(
            parent=msg["object_id"],
            position=(-.5, 0, -.5),
            scale=(0.05, 0.05, 0.05)
        )
        circle2 = Circle(
            parent=msg["object_id"],
            position=(.5, 0, -.5),
            scale=(0.05, 0.05, 0.05),
            ttl=5
        )
        scene.add_object(circle1)
        scene.add_object(circle2)

scene.new_obj_callback = new_obj_callback

print("Go to URL: https://arena.andrew.cmu.edu/example")

# our main event loop
scene.run_tasks()
