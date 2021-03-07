# camera-tracer.py
''' Camera tracing program. Draws a path that follows the user.
'''

from arena import *


LINE_COLOR = "#abcdef"


class CameraState(Object):
    def __init__(self):
        self.camera = None
        self.prev_pos = None

    def add_cam(self, camera):
        if not self.camera: # add camera if it doesnt exist already
            self.camera = camera

    @property
    def curr_pos(self):
        if self.camera:
            return self.camera.data.position

    @property
    def displacement(self):
        if self.prev_pos:
            return self.prev_pos.distance_to(self.curr_pos)
        else:
            return 0


lines = []
cam_state = CameraState()

def user_join_callback(scene, cam, msg):
    print(cam)
    cam_state.add_cam(cam)

arena = Scene(host="arena.andrew.cmu.edu", realm="realm", scene="example")
arena.user_join_callback = user_join_callback


def line_follow():
    if cam_state.displacement >= 0.5:
        line = ThickLine(color=LINE_COLOR, path=(cam_state.prev_pos, cam_state.curr_pos), lineWidth=5)
        arena.add_object(line)

        lines.append(line)
        if len(lines) > 30:
            arena.delete_object(lines.pop(0))

    # the camera's position gets automatically updated by arena-py!
    cam_state.prev_pos = cam_state.curr_pos

arena.run_forever(line_follow, 500)

arena.run_tasks() # will block
