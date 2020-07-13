# volatile.py
''' Demonstrate setting apriltags which can receive external updates.
    The apriltag 450 must be visible from a webxr browser camera.
    View: https://xr.andrew.cmu.edu/?scene=external&localTagSolver=true
'''
import arena

arena.init("oz.andrew.cmu.edu", "realm", "volatile")
# TAG = arena.Object(objName="apriltag_450",
#                    data='{"material": {"transparent": true, "opacity": 0}}',
#                    volatile=True)
# arena.Object(objName="duck",
#              objType=arena.Shape.gltf_model,
#              scale=(0.1, 0.1, 0.1),
#              rotation=(0.7, 0, 0, 0.7),
#              parent=TAG.objName,
#              url="models/Duck.glb",
#              volatile=True)
arena.Object(objName="apriltag_450",
             objType=arena.Shape.text,
             color=(255, 0, 0),
             volatile=True)

# our main event loop
arena.handle_events()
