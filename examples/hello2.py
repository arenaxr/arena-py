# hello2.py
# demonstrate receiving ARENA callback (JSON) messages

import arena


def scene_callback(msg):
    print("scene_callback: ", msg)


arena.init("arena.andrew.cmu.edu", "realm", "example", scene_callback)

# synchronous draw commands
cube = arena.Object(objType=arena.Shape.cube, clickable=True)

# our main event loop
arena.handle_events()
