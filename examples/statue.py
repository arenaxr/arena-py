# statue.py
""" Sample scene: Toggle button with 3d model.
    Example of setting up and activating interactive animation.
"""
import argparse

from arena import GLTF, Animation, Scene, Text

# general defaults
MQTTH = "arenaxr.org"  # -r hostname
NSPACE = "npereira"  # -n namespace
SCENE = "statue"  # -s scenename
POSITION = (0, 0, -2)  # -p pos.x pos.y pos.z
ROTATION = (0, 0, 0)  # -r rot.x rot.y rot.z

# command line options
parser = argparse.ArgumentParser()
parser.add_argument("-p", "--position", nargs=3, type=int, default=POSITION)
parser.add_argument("-r", "--rotation", nargs=3, type=int, default=ROTATION)
parser.add_argument("-mh", "--mqtth", type=str, default=MQTTH)
parser.add_argument("-s", "--scene", type=str, default=SCENE)
parser.add_argument("-n", "--namespace", type=str, default=NSPACE)
args = parser.parse_args()
app_position = tuple(args.position)
app_rotation = tuple(args.rotation)

# app variables
statue = None
started_rotate = False
statue_start_scale = (.05, .05, .05)
statue_scale = (.05, .05, .05)
button_scale = (.3, .3, .3)
text_scale_child = (1, 1, 1)
button_position = app_position
statue_position = (app_position[0], app_position[1]+.6, app_position[2])
statue_hide_position = (app_position[0], app_position[1]-10, app_position[2])
statue_hide_scale = (.0001, .0001, .0001)
text_position_child = (0, .5, -1)


def end_program_callback(scene: Scene):
    global statue, start_btn, start_txt
    scene.delete_object(statue)
    scene.delete_object(start_btn)
    scene.delete_object(start_txt)


arena = Scene(
    host=args.mqtth,
    namespace=args.namespace,
    scene=args.scene,
    end_program_callback=end_program_callback,
)


def start_click(scene: Scene, evt, msg):
    global statue
    global started_rotate

    if evt.type == "mouseup":
        if started_rotate:
            scene.update_object(
                statue,
                scale=statue_hide_scale,
                position=statue_hide_position,
            )
            started_rotate = False
            return

        statue = GLTF(
            object_id="gltf-les_bourgeois_de_calais_by_rodin",
            scale=statue_hide_scale,
            position=statue_position,
            url="/store/users/wiselab/models/les_bourgeois_de_calais_by_rodin/les_bourgeois_de_calais_by_rodin.gltf"
        )
        scene.add_object(statue)

        scene.update_object(
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

        scene.update_object(statue, clickable=True, evt_handler=start_rotate)


def start_rotate(scene: Scene, evt, msg):
    global started_rotate
    global statue

    if not started_rotate:
        scene.update_object(
            statue,
            animation=Animation(
                property="rotation",
                pauseEvents="mouseleave",
                resumeEvents="mouseenter",
                end=(0, 360, 0),
                loop=True,
                dur=20000,
                easing="linear"
            ),
            scale=statue_scale
        )
        started_rotate = True


@arena.run_once
def main():
    global statue, start_btn, start_txt

    # Create models
    start_btn = GLTF(
        object_id="gltf-start_btn",
        position=button_position,
        rotation=args.rotation,
        scale=button_scale,
        url="/store/users/wiselab/models/button-lowpoly/button.gltf",
        persist=True
    )
    arena.add_object(start_btn)
    arena.update_object(start_btn, clickable=True, evt_handler=start_click)

    start_txt = Text(
        object_id="gltf-start_txt",
        position=text_position_child,
        parent=start_btn.object_id,
        scale=text_scale_child,
        text="Click and hover on the button to run some interactive networked Python code.",
        persist=True
    )
    arena.add_object(start_txt)

    statue = GLTF(
        object_id="gltf-les_bourgeois_de_calais_by_rodin",
        scale=statue_hide_scale,
        position=statue_hide_position,
        rotation=args.rotation,
        url="/store/users/wiselab/models/les_bourgeois_de_calais_by_rodin/les_bourgeois_de_calais_by_rodin.gltf"
    )
    arena.add_object(statue)


arena.run_tasks()
