# earth-moon-simple.py
''' Simple program to animate the earth and moon. '''
from arena import *
scene = Scene(host="arenaxr.org", scene="earth")
earth = GLTF(object_id="gltf-model_Earth",
            scale=(10, 10, 10),
            url="store/users/wiselab/models/Earth.glb",
            animation=Animation(property="rotation",
                                end=(0, 360, 0),
                                loop=True,
                                dur=20000,
                                easing="linear"))
moon = GLTF(object_id="gltf-model_Moon",
            position=(0, 0.05, 0.6),
            scale=(0.05, 0.05, 0.05),
            url="store/users/wiselab/models/Moon.glb",
            parent="gltf-model_Earth",
            animation=Animation(property="scale",
                                start=(0.05, 0.05, 0.05),
                                end=(0.1, 0.1, 0.1),
                                startEvents="click",
                                loop=6,
                                dur=1000,
                                dir="alternate",
                                easing="easeInOutCirc"))
scene.add_object(earth)
scene.add_object(moon)
scene.run_tasks()
