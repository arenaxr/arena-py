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
