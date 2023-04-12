# earth-moon.py
''' Sample scene: Earth and Moon with Markers.
    Example of setting up and activating interactive animation.
'''
from arena import *

persist=True

MARKER_SCALE = 0.15
OPC_ON=0.85
OPC_OFF=0.25

def end_program_callback(scene: Scene):
    global sceneParent
    scene.delete_object(sceneParent)


# command line options
#scene = Scene(cli_args=True, end_program_callback=end_program_callback)
scene = Scene(
    cli_args=True, end_program_callback=end_program_callback, debug=True)


@scene.run_once
def main():
    addobjects()


def addobjects():
    global sceneParent, origin_marker
    # make a parent scene object
    sceneParent = Entity(
        persist=persist,
        object_id="callibrateParent",
        position=Position(0, 0, 0),
    )
    scene.add_object(sceneParent)

    origin_marker = GLTF(
        persist=persist,
        object_id="origin-marker",
        parent=sceneParent.object_id,
        url="/store/public/armarker.glb",
        rotation=Rotation(w=0.70711, x=-0.70711, y=0, z=0),
        scale=Scale(MARKER_SCALE, MARKER_SCALE, MARKER_SCALE),
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

    cone_scale = Scale(MARKER_SCALE/10, MARKER_SCALE/10*2, MARKER_SCALE/10)
    scene.add_object(Cone(
        persist=persist,
        object_id="click-position-y-pos",
        parent=sceneParent.object_id,
        rotation=Rotation(0, 0, 0),
        scale=cone_scale,
        position=Position(0, MARKER_SCALE+(MARKER_SCALE/10), 0),
        material=Material(color=Color(0, 0, 255), opacity=OPC_OFF),
        clickable=True,
        evt_handler=mouse_position_handler,
    ))
    scene.add_object(Cone(
        persist=persist,
        object_id="click-position-y-neg",
        parent=sceneParent.object_id,
        rotation=Rotation(180, 0, 0),
        scale=cone_scale,
        position=Position(0, MARKER_SCALE-(MARKER_SCALE/10), 0),
        material=Material(color=Color(0, 0, 255), opacity=OPC_OFF),
        clickable=True,
        evt_handler=mouse_position_handler,
    ))


def mouse_position_handler(scene, evt, msg):

    obj = scene.all_objects[evt.object_id]
    parts = evt.object_id.split("-")
    if evt.type == "mouseenter":
        scene.update_object(obj, material=Material(color=Color(0, 0, 255), opacity=OPC_ON))
    elif evt.type == "mouseleave":
        scene.update_object(obj, material=Material(color=Color(0, 0, 255), opacity=OPC_OFF))
    elif evt.type == "mousedown":
        camera_position_updater(cam_id=evt.data.source, dir=parts[3], axis=parts[2])


def camera_position_updater(cam_id, dir, axis):
    # publish something here
    print(f'logged position request :{cam_id}:{dir}:{axis}:')


scene.run_tasks()
