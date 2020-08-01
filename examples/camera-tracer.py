# volatile.py
''' Demonstrate setting a callback for a particular camera. 
'''
import arena
from scipy.spatial import distance

SCENE = "tracer"
fixedCamera = "test"

last_position = [0.0,0.0,0.0]

def camera_callback(event=None):
    global last_position

    cam_moved = distance.euclidean(event.position,last_position)
    if cam_moved > 0.25:
        last_position = event.position
        arena.Object(objType=arena.Shape.sphere,location=event.position,scale = (0.1, 0.1, 0.1),color=(255,0,0))
        print( "Draw Ball")

arena.init("oz.andrew.cmu.edu", "realm", SCENE )


cameraStr = "camera_" + fixedCamera + "_" + fixedCamera

my_camera = arena.Object(objName=cameraStr,
                   transparency=arena.Transparency(True, 0),
                   callback=camera_callback,
                   persist=False)

print( "Go to URL: https://xr.andrew.cmu.edu/?scene=" + SCENE +  "&fixedCamera=" + fixedCamera)

# our main event loop
arena.handle_events()
