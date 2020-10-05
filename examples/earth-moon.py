# earth-moon.py
''' Sample scene: Earth and Moon with Markers.
    Example of setting up and activating interactive animation.
'''
import arena

arena.init("arena.andrew.cmu.edu", "realm", "example")
# Create models
earth = arena.Object(
    objName="gltf-model_Earth", objType=arena.Shape.gltf_model,
    location=(0, 0.1, 0), scale=(5, 5, 5),
    url="models/Earth.glb")
moon = arena.Object(
    objName="gltf-model_Moon", objType=arena.Shape.gltf_model,
    location=(0, 0.05, 0.6), scale=(0.05, 0.05, 0.05),
    url="models/Moon.glb", parent="gltf-model_Earth")
# Define animation and movement
earth.update(
    data='{"animation": { "property": "rotation", "to": "0 360 0", "loop": true, "dur": 20000, "easing": "linear"}}')
earth.update(
    data='{"startEvents": "click", "property": "scale", "dur": 1000, "from": "10 10 10", "to": "5 5 5", "easing": "easeInOutCirc", "loop": 5, "dir": "alternate"}')
# Add a click-listener
earth.update(clickable=True)
# Create marker objects
arena.Object(objName="box0", color=(0, 0, 255), scale=(0.2, 0.2, 0.2))
arena.Object(objName="box1", color=(255, 0, 0), scale=(0.2, 0.2, 0.2),
             location=(-0.7,  1.67, 2.11))
arena.Object(objName="box2", color=(255, 0, 0), scale=(0.2, 0.2, 0.2),
             location=(-2.88, 2.80, -2.12))
arena.Object(objName="box3", color=(255, 0, 0), scale=(0.2, 0.2, 0.2),
             location=(-0.09, 1.30, -3.66))
arena.Object(objName="box4", color=(255, 0, 0), scale=(0.2, 0.2, 0.2),
             location=(3.31, 2.00, -0.97))

arena.handle_events()
