# Advanced Example - EVEN more functionality!

## User management
An ARENA-py Scene keep tracks of all incoming and outgoing users. Users are stored as camera objects. Get a list of all users in a scene like so:
```python
scene.get_user_list()
# returns [Camera(object_id="camera_1234556789_Edward"), Camera(object_id="camera_987654321_Ed"), ...]
```

Scenes also have special user callbacks. user_join_callback is called whenever a user is found by the library:
```python
def user_join_callback(scene, cam, msg):
    # do stuff here
    # cam is Camera object
    pass

scene.user_join_callback = user_join_callback
```

## Printing objects/looking at JSON
All objects are printed as JSON/python dictionaries. So to make sure your JSON is formatted correctly,
```python
print(cam) # will print as a dict
print(scene.update_object(box, position=Position(1,1,1))) # will print what was published as a dict
```

## Objects get automatically updated
You can leverage the fact that Objects in ARENA-py get automatically updated to do some cool things! Lets make a camera tracer program that traces the movement of users in a scene.

## Camera Tracer
Lets start by creating a helper class that stores the camera and the previous position of the camera:
```python
class CameraState(Object):
    def __init__(self, camera):
        self.camera = camera
        self.prev_pos = None
        self.line_color = Color(
                random.randint(0,255),
                random.randint(0,255),
                random.randint(0,255)
            )

    @property
    def curr_pos(self):
        # camera position is not static, it is constantly changing and will be updated in real-time
        return self.camera.data.position

    @property
    def displacement(self):
        if self.prev_pos:
            # Position attributes have a distance_to method that returns the distance to another Position
            return self.prev_pos.distance_to(self.curr_pos)
        else:
            return 0
```

Then, lets maintain a list of all camera states in a scene:
```python
cam_states = []

# called whenever a user is found by the library
def user_join_callback(scene, cam, msg):
    global cam_states

    cam_state = CameraState(cam)
    cam_states += [cam_state]
```

## Object Time to Live (TTL)
The `ttl` attribute of an object can set the amount of time (in seconds) that an object will stay in the scene until it is automatically deleted by the browser client.
```python
line = ThickLine(
        color="#123456",
        path=(Position(0,0,0), Position(10,10,10)),
        ttl=3 # live for 3 seconds
    )
```

## Camera Tracer
Lastly, lets have a loop that checks if a camera has displaced a certain distance, then draw a line that lasts for 3 seconds if it did:
```python
MIN_DISPLACEMENT = 0.5
LINE_TTL = 5

@scene.run_forever(interval_ms=200)
def line_follow():
    for cam_state in cam_states:
        if cam_state.displacement >= MIN_DISPLACEMENT:
            line = ThickLine(
                    color=cam_state.line_color,
                    path=(cam_state.prev_pos, cam_state.curr_pos),
                    lineWidth=3,
                    ttl=LINE_TTL
                )
            scene.add_object(line)

        # the camera's position gets automatically updated by arena-py!
        cam_state.prev_pos = cam_state.curr_pos
```

# Appendix
```python
from arena import *
import random

MIN_DISPLACEMENT = 0.5
LINE_TTL = 5

class CameraState(Object):
    def __init__(self, camera):
        self.camera = camera
        self.prev_pos = None
        self.line_color = Color(
                random.randint(0,255),
                random.randint(0,255),
                random.randint(0,255)
            )

    @property
    def curr_pos(self):
        # camera position is not static, it is constantly changing and will be updated in real-time
        return self.camera.data.position

    @property
    def displacement(self):
        if self.prev_pos:
            # Position attributes have a distance_to method that returns the distance to another Position
            return self.prev_pos.distance_to(self.curr_pos)
        else:
            return 0

cam_states = []

# called whenever a user is found by the library
def user_join_callback(scene, cam, msg):
    global cam_states

    cam_state = CameraState(cam)
    cam_states += [cam_state]

scene = Scene(host="arenaxr.org", realm="realm", scene="example")
scene.user_join_callback = user_join_callback

@scene.run_forever(interval_ms=200)
def line_follow():
    for cam_state in cam_states:
        if cam_state.displacement >= MIN_DISPLACEMENT:
            line = ThickLine(
                    color=cam_state.line_color,
                    path=(cam_state.prev_pos, cam_state.curr_pos),
                    lineWidth=3,
                    ttl=LINE_TTL
                )
            scene.add_object(line)

        # the camera's position gets automatically updated by arena-py!
        cam_state.prev_pos = cam_state.curr_pos

scene.run_tasks()
```
