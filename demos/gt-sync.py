''' Synchronize users for ground truth collection with apriltags
'''
import arena
import sys
import getopt

broker = 'oz.andrew.cmu.edu'
realm = 'realm'
scene = 'cic-tags'
COLOR_WALK = (0, 255, 0)
COLOR_FINDTAG = (255, 0, 0)
COLOR_WAIT = (255, 255, 0)

def printhelp():
    print('gt-sync.py [-s <scene>] <user1> [user2 ...]')
    print('   ex: python3 gt-sync.py -s myScene name1 name2 name3')

try:
    opts, args = getopt.getopt(sys.argv[1:], 'hs:', ['scene='])
except getopt.GetoptError:
    printhelp()
    sys.exit(2)

for opt, arg in opts:
    if opt == '-h':
        printhelp()
        sys.exit()
    elif opt in ('-s', '--scene'):
        scene = arg

if len(args) < 1:
    printhelp()
    sys.exit(2)

print("Scene: " + scene)
print("Users: " + args)

# arena.init(broker, realm, scene)
# obj_str = "circle_" + user
# camera_str = "camera_" + user + "_" + user
# arena.Object(objName=obj_str,
#              objType=arena.Shape.circle,
#              parent=camera_str,
#              location=(-.5, 0, -.5),
#              rotation=(0, 0, 0, 1),
#              scale=(0.05, 0.05, 0.05),
#              color=color,
#              persist=True)

# print("Go to URL: https://xr.andrew.cmu.edu/?scene=" + scene + "&fixedCamera=" + user)

# # our main event loop
# arena.handle_events()
