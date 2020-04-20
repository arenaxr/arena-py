# hello3.py
# demonstrate setting arbitrary (animation) JSON data
# - animates rotating duck
import arena

arena.init("oz.andrew.cmu.edu", "realm", "hello")
arena.Object(objType=arena.Shape.cube)
arena.Object(objType=arena.Shape.sphere,location=(1,1,-1),color=(255,0,0))
arena.Object(objType=arena.Shape.gltf_model,
             location=(-1,1,-3),
             persist=False,
             physics=arena.Physics.none,
             clickable=True,
             data='{"animation": { "property": "rotation", "to": "0 360 0", "loop": true, "dur": 10000}}',
             url="models/Duck.glb")

# our main event loop
arena.handle_events()
