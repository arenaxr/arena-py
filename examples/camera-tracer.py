# volatile.py
''' Demonstrate setting a callback for a particular camera. 
'''
import arena
import sys, getopt
from scipy.spatial import distance

SCENE = "tracer"
fixedCamera = "test"

last_position = [0.0,0.0,0.0]
cam_color = (255,0,0)

def camera_callback(event=None):
    global last_position
    global cam_color

    cam_moved = distance.euclidean(event.position,last_position)
    if cam_moved > 0.25:
        last_position = event.position
        arena.Object(objType=arena.Shape.sphere,location=event.position,scale = (0.1, 0.1, 0.1),color=cam_color)
        print( "Draw Marker")



try:
    opts, args = getopt.getopt(sys.argv[1:],"hs:u:c:",["scene=","user=","color="])
except getopt.GetoptError:
    print( "tracer.py -s <scene> -u <fixedCamera> -c <r,g,b> " )
    print( "   ex: python3 tracer.py -s myScene -u myCamera -c 255,0,0" )
    sys.exit(2)

for opt, arg in opts:
    if opt == '-h':
        print( "tracer.py -s <scene> -u <fixedCamera> -c <r,g,b> " )
        print( "   ex: python3 tracer.py -s myScene -u myCamera -c 255,0,0" )
        sys.exit()
    elif opt in ("-s", "--scene"):
        SCENE = arg
    elif opt in ("-u", "--user"):
        fixedCamera = arg
    elif opt in ("-c", "--color"):
        cam_color = arg.split(',')


print("Scene: " + SCENE)
print("fixedCamera: " + fixedCamera)
print("color: " + str(cam_color))

arena.init("oz.andrew.cmu.edu", "realm", SCENE )
cameraStr = "camera_" + fixedCamera + "_" + fixedCamera

my_camera = arena.Object(objName=cameraStr,
                   transparency=arena.Transparency(True, 0),
                   callback=camera_callback,
                   persist=False)

print( "Go to URL: https://xr.andrew.cmu.edu/?scene=" + SCENE +  "&fixedCamera=" + fixedCamera)

# our main event loop
arena.handle_events()
