# earth-moon.py
''' Sample scene: Earth and Moon with Markers.
    Example of setting up and activating interactive animation.
'''
from arena import *

persist = True

MARKER_SCALE = 0.15
OPC_ON = 0.85
OPC_OFF = 0.25


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
    # parent scene object
    sceneParent = Entity(
        persist=persist,
        object_id="callibrateParent",
        position=Position(0, 0, 0),
    )
    scene.add_object(sceneParent)

    # marker gltf
    origin_marker = GLTF(
        persist=persist,
        object_id="origin-marker",
        parent=sceneParent.object_id,
        url="/store/public/armarker.glb",
        rotation=Rotation(w=0.70711, x=-0.70711, y=0, z=0),
        scale=Scale(MARKER_SCALE, MARKER_SCALE, MARKER_SCALE),
    )
    armarker = {
        "markerid": 0,
        "markertype": "apriltag_36h11",
        "size": 150,
        "buildable": False,
        "dynamic": False
    }
    scene.update_object(origin_marker, armarker=armarker)

    add_pos("x")
    add_pos("y")
    add_pos("z")


def get_color(direction):
    if direction == "x":
        return Color(0, 255, 0)
    elif direction == "y":
        return Color(0, 0, 255)
    elif direction == "z":
        return Color(255, 0, 0)


def add_pos(direction):
    if direction == "x":
        position = Position(MARKER_SCALE/2, 0, 0)
        rotation = Rotation(0, 0, -90)
    elif direction == "y":
        position = Position(0, MARKER_SCALE/2, 0)
        rotation = Rotation(0, 0, 0)
    elif direction == "z":
        position = Position(0,  0, MARKER_SCALE/2)
        rotation = Rotation(90, 0, 0)
    click = Entity(
        persist=persist,
        object_id=f"click-{direction}",
        parent=sceneParent.object_id,
        rotation=rotation,
        position=position,
        height=MARKER_SCALE/10,
        radiusBottom=MARKER_SCALE/10/2,
    )
    scene.add_object(click)
    # position cones
    cone_scale = Scale(MARKER_SCALE/10, MARKER_SCALE/10*2, MARKER_SCALE/10)
    scene.add_object(Cone(
        persist=persist,
        object_id=f"click-position-{direction}-pos",
        parent=click.object_id,
        rotation=Rotation(0, 0, 0),
        scale=cone_scale,
        position=Position(0, (MARKER_SCALE/2)+(MARKER_SCALE/10), 0),
        material=Material(color=get_color(direction), opacity=OPC_OFF),
        clickable=True,
        evt_handler=mouse_position_handler,
    ))
    scene.add_object(Cone(
        persist=persist,
        object_id=f"click-position-{direction}-neg",
        parent=click.object_id,
        rotation=Rotation(180, 0, 0),
        scale=cone_scale,
        position=Position(0, (MARKER_SCALE/2)-(MARKER_SCALE/10), 0),
        material=Material(color=get_color(direction), opacity=OPC_OFF),
        clickable=True,
        evt_handler=mouse_position_handler,
    ))


def mouse_position_handler(scene, evt, msg):

    obj = scene.all_objects[evt.object_id]
    parts = evt.object_id.split("-")
    direction = parts[2]
    axis = parts[3]
    if evt.type == "mouseenter":
        scene.update_object(obj, material=Material(
            color=get_color(direction), opacity=OPC_ON))
    elif evt.type == "mouseleave":
        scene.update_object(obj, material=Material(
            color=get_color(direction), opacity=OPC_OFF))
    elif evt.type == "mousedown":
        camera_position_updater(evt.data.source, direction, axis)


def camera_position_updater(cam_id, direction, axis):
    # publish something here
    print(f'logged position request :{cam_id}:{direction}:{axis}:')


def camera_rotation_updater(cam_id, direction, axis):
    # publish something here
    print(f'logged rotation request :{cam_id}:{direction}:{axis}:')


scene.run_tasks()
