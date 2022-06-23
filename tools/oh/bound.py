'''
bound.py
   Demonstrates constraining user to specified bounds
'''
from arena import *
import math

scene = Scene(host="mqtt.arenaxr.org", realm="realm", scene="example")

'''
   Determines whether or not user is within bounds
   @param center:   center of boundary
   @param r:        radius from center to edge of boundaries
   @param pos:      user's position
'''
def check_out_bounds(center, r, pos):
    cx = center[0]
    cy = center[1]
    px = pos[0]
    py = pos[1]
    return py > cy + r or py < cy -r or px < cx - r or px > cx + r

def bound(center, radius):
    for user in scene.users.values():
        pos = user['data']['position']
        x = pos['x']
        z = pos['z']
        if check_out_bounds((0,0),10,(x,z)):
            scene.manipulate_camera(
                user,
                position= center
            )

@scene.run_forever(interval_ms=1000)
def main():
    global scene
    bound(Position(0,2,0), 1)

scene.run_tasks()
