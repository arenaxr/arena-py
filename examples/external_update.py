# external_update.py
''' Demonstrate setting apriltags which can receive external updates.
    The apriltag 450 must be visible from a webxr browser camera.
    View: https://xr.andrew.cmu.edu/?scene=external&localTagSolver=true
'''
import arena

arena.init("oz.andrew.cmu.edu", "realm", "external")
arena.Object(objName="apriltag_450",
             objType=arena.Shape.gltf_model,
             scale=(0.1, 0.1, 0.1),
             rotation=(0, 0, 0, 1),
             persist=True,
             url="models/Duck.glb")

# our main event loop
arena.handle_events()
