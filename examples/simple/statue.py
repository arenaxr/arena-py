"""Statue

Sample scene: Toggle button with 3d model.
Example of setting up and activating interactive animation.
"""

from arena import *


def end_program_callback(scene):
    global sceneParent
    scene.delete_object(sceneParent)


# command line options
arena = Scene(cli_args=True, end_program_callback=end_program_callback)
app_position = arena.args["position"]
app_rotation = arena.args["rotation"]
app_scale = arena.args["scale"]

# app variables
statue = None
started_rotate = False
statue_start_scale = (.05, .05, .05)
statue_scale = (.05, .05, .05)
button_scale = (.3, .3, .3)
statue_position = (0, .6, 0)
statue_hide_position = (0, -10, 0)
statue_hide_scale = (.0001, .0001, .0001)


def start_click(scene, evt, msg):
    global statue, started_rotate

    if evt.type == "mouseup":
        if started_rotate:
            scene.update_object(
                statue,
                scale=statue_hide_scale,
                position=statue_hide_position,
            )
            started_rotate = False
            return

        scene.update_object(
            statue,
            scale=statue_hide_scale,
            position=statue_position,
        )

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


def start_rotate(scene, evt, msg):
    global started_rotate, statue

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
    global sceneParent, statue, start_btn, start_txt
    # make a parent scene object
    sceneParent = Object(
        persist=True,
        object_id="statue-sceneParent",
        position=app_position,
        rotation=app_rotation,
        scale=app_scale,
    )
    arena.add_object(sceneParent)

    # Create models
    start_btn = GLTF(
        object_id="statue-start_btn",
        position=(0, .1, 1.5),
        scale=button_scale,
        url="/store/users/wiselab/models/button-lowpoly/button.gltf",
        parent=sceneParent.object_id,
        persist=True,
    )
    arena.add_object(start_btn)
    arena.update_object(start_btn, clickable=True, evt_handler=start_click)

    start_txt = Text(
        object_id="statue-start_txt",
        position=(0, .75, 1),
        value="Click and hover on the button to run some interactive networked Python code.",
        color="#555555",
        persist=True,
        parent=sceneParent.object_id,
    )
    arena.add_object(start_txt)

    statue = GLTF(
        object_id="statue-gltf-les_bourgeois_de_calais_by_rodin",
        scale=statue_hide_scale,
        position=statue_hide_position,
        url="/store/users/wiselab/models/les_bourgeois_de_calais_by_rodin/les_bourgeois_de_calais_by_rodin.gltf",
        parent=sceneParent.object_id,
    )
    arena.add_object(statue)


arena.run_tasks()
