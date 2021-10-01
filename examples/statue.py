# earth-moon.py
''' Sample scene: Earth and Moon with Markers.
    Example of setting up and activating interactive animation.
'''
from arena import *

arena = Scene(host="arenaxr.org", realm="realm", namespace="npereira", scene="statue")

statue = None
started_rotate = False

statue_start_scale = (.05, .05, .05)
statue_scale = (.05, .05, .05)
statue_position = (0, .6, 0)
button_position = (0, 0, 0)

def start_click(scene, evt, msg):
    global arena
    global statue
    global started_rotate

    if (evt.type == 'mouseup'):
        if (started_rotate == True):
            arena.update_object(
                statue,
                scale=(.0001, .0001, .0001),
                position=(0, -10, 0),
            )
            started_rotate = False
            return

        statue = GLTF(
                object_id="gltf-les_bourgeois_de_calais_by_rodin",
                scale=(.0001, .0001, .0001),
                position=statue_position,
                url="/store/users/wiselab/models/les_bourgeois_de_calais_by_rodin/les_bourgeois_de_calais_by_rodin.gltf"
        )

        arena.add_object(statue)

        arena.update_object(
            statue,
            animation=Animation(
                property="scale",
                start=statue_start_scale, end=statue_scale,
                loop=1,
                dur=1000,
                dir="linear",
                easing="easeInOutCirc"
            ),
            clickable=True
        )

        arena.update_object(statue, clickable=True, evt_handler=start_rotate)

def start_rotate(scene, evt, msg):
    global started_rotate
    global statue
    global arena

    if started_rotate == False:
        arena.update_object(
            statue,
            animation=Animation(
                property="rotation",
                pauseEvents="mouseleave",
                resumeEvents="mouseenter",
                end=(0,360,0),
                loop=True,
                dur=20000,
                easing="linear"
            ),
            scale=statue_scale
        )
        started_rotate = True

@arena.run_once
def main():
    global statue

    # Create models
    start_btn = GLTF(
            object_id="gltf-start_btn",
            position=button_position,
            scale=(.3, .3, .3),
            url="/store/users/wiselab/models/button-lowpoly/button.gltf",
            persist=True
        )

    arena.add_object(start_btn)
    arena.update_object(start_btn, clickable=True, evt_handler=start_click)

    statue = GLTF(
            object_id="gltf-les_bourgeois_de_calais_by_rodin",
            scale=(.0001, .0001, .0001),
            position=(0, -10, 0),
            url="/store/users/wiselab/models/les_bourgeois_de_calais_by_rodin/les_bourgeois_de_calais_by_rodin.gltf"
    )

    arena.add_object(statue)

arena.run_tasks()
