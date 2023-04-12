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
    add_axis("x")
    add_axis("y")
    add_axis("z")


def get_color(axis):
    if axis == "x":
        return Color(0, 255, 0)
    elif axis == "y":
        return Color(0, 0, 255)
    elif axis == "z":
        return Color(255, 0, 0)


def add_axis(axis):
    if axis == "x":
        position = Position(MARKER_SCALE/2, 0, 0)
        rotation = Rotation(0, 90, -90)
    elif axis == "y":
        position = Position(0, MARKER_SCALE/2, 0)
        rotation = Rotation(0, 0, 0)
    elif axis == "z":
        position = Position(0,  0, MARKER_SCALE/2)
        rotation = Rotation(90, 0, 0)
    # click root
    click = Entity(
        persist=persist,
        object_id=f"click-{axis}",
        parent=sceneParent.object_id,
        rotation=rotation,
        position=position,
        height=MARKER_SCALE/10,
        radiusBottom=MARKER_SCALE/10/2,
    )
    scene.add_object(click)
    # position
    cone_scale = Scale(MARKER_SCALE/10, MARKER_SCALE/10*2, MARKER_SCALE/10)
    scene.add_object(Cone(
        persist=persist,
        object_id=f"click-position-{axis}-pos",
        parent=click.object_id,
        scale=cone_scale,
        rotation=Rotation(0, 0, 0),
        position=Position(0, (MARKER_SCALE/2)+(MARKER_SCALE/10), 0),
        material=Material(color=get_color(
            axis), opacity=OPC_OFF),
        clickable=True,
        evt_handler=mouse_handler,
    ))
    scene.add_object(Cone(
        persist=persist,
        object_id=f"click-position-{axis}-neg",
        parent=click.object_id,
        scale=cone_scale,
        rotation=Rotation(180, 0, 0),
        position=Position(0, (MARKER_SCALE/2)-(MARKER_SCALE/10), 0),
        material=Material(color=get_color(
            axis), opacity=OPC_OFF),
        clickable=True,
        evt_handler=mouse_handler,
    ))
    # rotation
    scene.add_object(Cone(
        persist=persist,
        object_id=f"click-rotation-{axis}-pos",
        parent=click.object_id,
        scale=cone_scale,
        rotation=Rotation(90, 0, 0),
        position=Position(MARKER_SCALE/10, 0, 0),
        material=Material(color=get_color(axis),
                          opacity=OPC_OFF),
        clickable=True,
        evt_handler=mouse_handler,
    ))
    scene.add_object(Cone(
        persist=persist,
        object_id=f"click-rotation-{axis}-neg",
        parent=click.object_id,
        scale=cone_scale,
        rotation=Rotation(-90, 0, 0),
        position=Position(-MARKER_SCALE/10, 0, 0),
        material=Material(color=get_color(axis),
                          opacity=OPC_OFF),
        clickable=True,
        evt_handler=mouse_handler,
    ))


def mouse_handler(scene, evt, msg):

    obj = scene.all_objects[evt.object_id]
    parts = evt.object_id.split("-")
    attribute = parts[1]
    axis = parts[2]
    direction = parts[3]
    if evt.type == "mouseenter":
        scene.update_object(obj, material=Material(
            color=get_color(axis), opacity=OPC_ON))
    elif evt.type == "mouseleave":
        scene.update_object(obj, material=Material(
            color=get_color(axis), opacity=OPC_OFF))
    elif evt.type == "mousedown":
        if attribute == "position":
            camera_position_updater(evt.data.source, axis, direction)
        elif attribute == "rotation":
            camera_rotation_updater(evt.data.source, axis, direction)


def camera_position_updater(cam_id, axis, direction):
    # publish something here
    print(f'logged position request :{cam_id}:{direction}:{axis}:')


def camera_rotation_updater(cam_id, axis, direction):
    # publish something here
    print(f'logged rotation request :{cam_id}:{direction}:{axis}:')


scene.run_tasks()
