# earth-moon.py
''' Sample scene: Earth and Moon with Markers.
    Example of setting up and activating interactive animation.
'''
from arena import *

marker_scale = 0.15


def end_program_callback(scene: Scene):
    global sceneParent
    scene.delete_object(sceneParent)


# command line options
#scene = Scene(cli_args=True, end_program_callback=end_program_callback)
scene = Scene(
    cli_args=True, end_program_callback=end_program_callback, debug=True)


@scene.run_once
def main():
    global sceneParent, origin_marker
    # make a parent scene object
    sceneParent = Entity(
        persist=True,
        object_id="callibrateParent",
        material=Material(transparent=True, opacity=0),
    )
    scene.add_object(sceneParent)

    origin_marker = GLTF(
        persist=True,
        object_id="origin-marker",
        parent=sceneParent.object_id,
        url="/store/public/armarker.glb",
        position=Position(0, 0, 0),
        rotation=Rotation(w=0.70711, x=-0.70711, y=0, z=0),
        scale=Scale(marker_scale, marker_scale, marker_scale),
    )
    # scene.add_object(origin_marker)
    armarker = {
        "markerid": 0,
        "markertype": "apriltag_36h11",
        "size": 150,
        "buildable": False,
        "dynamic": False
    }
    scene.update_object(origin_marker, armarker=armarker)

    scene.add_object(Cone(
        persist=True,
        object_id="click-position-y-pos",
        parent=sceneParent.object_id,
        rotation=Rotation(0,0,0),
        scale=Scale(marker_scale/10, marker_scale/10*2, marker_scale/10),
        position=Position(0, marker_scale+(marker_scale/10), 0),
        material=Material(color=Color(0,0,255), transparent=False, opacity=0.5),
        clickable=True,
    ))
    scene.add_object(Cone(
        persist=True,
        object_id="click-position-y-neg",
        parent=sceneParent.object_id,
        rotation=Rotation(180,0,0),
        scale=Scale(marker_scale/10, marker_scale/10*2, marker_scale/10),
        position=Position(0, marker_scale-(marker_scale/10), 0),
        material=Material(color=Color(0,0,255), transparent=False, opacity=0.5),
        clickable=True,
    ))


scene.run_tasks()
