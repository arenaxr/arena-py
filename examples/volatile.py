# volatile.py
''' Demonstrate setting apriltags which can receive external updates.
    The apriltag #450 must be visible from a webxr browser camera.
    Position, Rotation, and Model should remain in sync across subscribers.
    Camera: https://arena.andrew.cmu.edu/volatile&localTagSolver=true&cvRate=10
    All: https://arena.andrew.cmu.edu/volatile
'''
# [TODO] update this to 0.1.0!
import arena


def tag_callback(event=None):
    ''' Since we expect the position/rotation updates, we can react here.
    '''
    if event.event_action == arena.EventAction.update and \
            event.event_type == arena.EventType.object:
        print("Tag position: " + str(event.position))
        print("Tag rotation: " + str(event.rotation))


arena.init("arena.andrew.cmu.edu", "realm", "example")
# apriltag_450 will receive position/rotation updates so don't set them
TAG = arena.Object(objName="apriltag_450",
                   transparency=arena.Transparency(True, 0),
                   callback=tag_callback,
                   persist=True)
# duck as child to it can can be rotated relative to apriltag
arena.Object(objName="duck",
             objType=arena.Shape.gltf_model,
             scale=(0.1, 0.1, 0.1),
             rotation=(0.7, 0, 0, 0.7),
             parent=TAG.objName,
             url="models/Duck.glb",
             persist=True)

# our main event loop
arena.handle_events()
