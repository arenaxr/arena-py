# volatile.py
''' Demonstrate setting apriltags which can receive external updates.
    The apriltag #450 must be visible from a webxr browser camera.
    Position, Rotation, and Model should remain in sync across cameras.
    # View: https://xr.andrew.cmu.edu/?scene=external&localTagSolver=true&camUpdateRate=16
'''
import arena

BROKER = "oz.andrew.cmu.edu"
REALM = "realm"
SCENE = "volatile"


arena.init(BROKER, REALM, SCENE)

# apriltag_450 will receive position/rotation updates so don't set them
TAG = arena.Object(objName="apriltag_450",
                   data='{"material": {"transparent": true, "opacity": 0}}',
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
