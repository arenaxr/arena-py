# volatile.py
''' Demonstrate setting an object to be a child of a camera 
'''
import arena
import sys
import getopt

scene = "cic-tags"
user = "test"
color = (0, 255, 0)


try:
    opts, args = getopt.getopt(sys.argv[1:], "hs:u:c:", [
                               "scene=", "user=", "color="])
except getopt.GetoptError:
    print("camera-child.py -s <scene> -u <user> -c <r,g,b> ")
    print("   ex: python3 camera-child.py -s myScene -u myName -c 255,0,0")
    sys.exit(2)

for opt, arg in opts:
    if opt == '-h':
        print("camera-child.py -s <scene> -u <user> -c <r,g,b> ")
        print("   ex: python3 camera-child.py -s myScene -u myCamera -c 255,0,0")
        sys.exit()
    elif opt in ("-s", "--scene"):
        scene = arg
    elif opt in ("-u", "--user"):
        user = arg
    elif opt in ("-c", "--color"):
        color = arg.split(',')


print("Scene: " + scene)
print("User: " + user)
print("Color: " + str(color))

arena.init("oz.andrew.cmu.edu", "realm", scene)
obj_str = "circle_" + user
camera_str = "camera_" + user + "_" + user
arena.Object(objName=obj_str,
             objType=arena.Shape.circle,
             parent=camera_str,
             location=(-.5, 0, -.5),
             rotation=(0, 0, 0, 1),
             scale=(0.05, 0.05, 0.05),
             color=color,
             persist=True)

print("Go to URL: https://xr.andrew.cmu.edu/?scene=" +
      scene + "&fixedCamera=" + user)

# our main event loop
arena.handle_events()
