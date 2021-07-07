# arb.py
#
# AR Builder
# Pass in args for scene name and/or broker and realm.

# pylint: disable=missing-docstring

# TODO: highlight mouseenter to avoid click
# TODO: fix follow unlock position relative, not default
# TODO: handle click-listener objects with 1.1 x scale shield?
# TODO: add easy doc overlay for each button operation

import argparse
import json
import math
import random
import statistics

from arena import (GLTF, Box, Circle, Color, Cone, Event, Line, Material,
                   Object, Position, Rotation, Scale, Scene, ThickLine)

import arblib
from arblib import (EVT_MOUSEDOWN, EVT_MOUSEENTER, EVT_MOUSELEAVE, ButtonType,
                    Mode)

BROKER = "arenaxr.org"
PORT = None
REALM = "realm"
NAMESPACE = None
SCENE = None  # no default scene, arb works on any scene
MANIFEST = arblib.DEF_MANIFEST
MODELS = []
USERS = {}  # dictionary of user instances
CONTROLS = {}  # dictionary of active controls
DEBUG = False
scene = None  # the global scene connection object
SCL_CLICK = 0.1  # meters


def init_args():
    global BROKER, PORT, REALM, NAMESPACE, SCENE, MODELS, MANIFEST, DEBUG
    parser = argparse.ArgumentParser(description='ARENA AR Builder.')
    parser.add_argument(
        'scene', type=str, help='ARENA scene name')
    parser.add_argument(
        '-n', '--namespace', type=str, help='ARENA namespace', default=NAMESPACE)
    parser.add_argument(
        '-b', '--broker', type=str, help='MQTT message broker hostname', default=BROKER)
    parser.add_argument(
        '-p', '--port', type=int, help='MQTT message broker port')
    parser.add_argument(
        '-r', '--realm', type=str, help='ARENA realm name', default=REALM)
    parser.add_argument(
        '-m', '--models', type=str, help='JSON GLTF manifest')
    parser.add_argument(
        '-d', '--debug', action='store_true', help='Debug mode.', default=False)
    args = parser.parse_args()
    print(args)
    SCENE = args.scene
    if args.debug:
        DEBUG = True
    if args.broker is not None:
        BROKER = args.broker
    if args.port is not None:
        PORT = args.port
    if args.realm is not None:
        REALM = args.realm
    if args.namespace is not None:
        NAMESPACE = args.namespace
    if args.models is not None:
        mfile = open(args.models)
        data = json.load(mfile)
        MODELS = []
        for i in data['models']:
            print(i)
        mfile.close()
        MANIFEST = data['models']
    for i in MANIFEST:
        MODELS.append(i['name'])


def handle_panel_event(event, dropdown=False):
    # naming order: camera_number_name_button_bname_dname
    drop = None
    obj = event.object_id.split("_")
    camname = event.data.source
    owner = f"{obj[0]}_{obj[1]}_{obj[2]}"  # callback owner in object_id
    if owner != camname:
        return None, None, None  # only owner may activate
    objid = event.object_id
    if event.type == EVT_MOUSEENTER or event.type == EVT_MOUSELEAVE:
        if event.type == EVT_MOUSEENTER:
            hover = True
        elif event.type == EVT_MOUSELEAVE:
            hover = False
        if dropdown:
            button = USERS[camname].dbuttons[objid].set_hover(hover)
        else:
            button = USERS[camname].panel[objid].set_hover(hover)

    if event.type != EVT_MOUSEDOWN:
        return None, None, None
    if dropdown:
        drop = obj[5]
    return (camname, objid, drop)


def handle_clip_event(event):
    # naming order: camera_number_name_object
    obj = event.object_id.split("_")
    camname = event.data.source
    owner = f"{obj[0]}_{obj[1]}_{obj[2]}"  # callback owner in object_id
    if owner != camname:
        return None  # only owner may activate
    if event.type != EVT_MOUSEDOWN:
        return None
    return camname


def handle_clickline_event(event, mode):
    camname = event.data.source
    val = 0
    # naming order: object-name_mode_axis-move_direction
    if USERS[camname].target_control_id and (event.type.startswith("twofinger") or USERS[camname].gesturing):
        ctrl_object_id = USERS[camname].target_control_id
    else:
        ctrl_object_id = event.object_id
    click_id = ctrl_object_id.split(f"_{mode.value}_")
    object_id = click_id[0]
    print(
        f"{ctrl_object_id} {event.type} g:{USERS[camname].gesturing} {USERS[camname].target_control_id}")
    # my-camera twofingerstart g:False None
    if not USERS[camname].target_control_id and not USERS[camname].gesturing and event.object_id == "my-camera":
        return None, None, None, val
    direction = (click_id[1])[0:2]
    move = (click_id[1])[1:4]
    if event.type == EVT_MOUSEENTER:
        if not USERS[camname].gesturing:
            scene.update_object(
                CONTROLS[object_id][ctrl_object_id],
                material=Material(transparent=True, opacity=arblib.OPC_CLINE_HOVER))
            # set controller target
            USERS[camname].target_control_id = ctrl_object_id
    elif event.type == EVT_MOUSELEAVE:
        if not USERS[camname].gesturing:
            scene.update_object(
                CONTROLS[object_id][ctrl_object_id],
                material=Material(transparent=True, opacity=arblib.OPC_CLINE))
            # release controller target
            USERS[camname].target_control_id = None

    # handle gestures
    elif event.type == "twofingerstart":
        # start hold down event for both clickers
        USERS[camname].gesturing = True
        scene.update_object(
            CONTROLS[object_id][f"{object_id}_{mode.value}_{(click_id[1])[0:1]}p{(click_id[1])[2:4]}"],
            material=Material(transparent=True, opacity=arblib.OPC_CLINE_HOVER))
        scene.update_object(
            CONTROLS[object_id][f"{object_id}_{mode.value}_{(click_id[1])[0:1]}n{(click_id[1])[2:4]}"],
            material=Material(transparent=True, opacity=arblib.OPC_CLINE_HOVER))
    elif event.type == "twofingerend":
        # release hold down event for both clickers
        if USERS[camname].gesturing:
            scene.update_object(
                CONTROLS[object_id][f"{object_id}_{mode.value}_{(click_id[1])[0:1]}p{(click_id[1])[2:4]}"],
                material=Material(transparent=True, opacity=arblib.OPC_CLINE))
            scene.update_object(
                CONTROLS[object_id][f"{object_id}_{mode.value}_{(click_id[1])[0:1]}n{(click_id[1])[2:4]}"],
                material=Material(transparent=True, opacity=arblib.OPC_CLINE))
            # release controller target
            USERS[camname].target_control_id = None
            USERS[camname].gesturing = False
    elif event.type == "twofingermove" and USERS[camname].slider:
        # send slider movement for clickers
        if USERS[camname].gesturing:
            obj = scene.get_persisted_obj(object_id)
            # determine direction of 2d gesture in 3d
            if click_id[1][0] == "y":
                val = event.data.positionStart.y - event.data.position.y
            elif click_id[1][0] == "x":
                if event.data.clickPos.z > obj.data.position.z:
                    val = event.data.positionStart.x - event.data.position.x
                else:
                    val = event.data.positionStart.x + event.data.position.x
            else:  # click_id[1][0] == "z":
                if event.data.clickPos.x < obj.data.position.x:
                    val = event.data.positionStart.x - event.data.position.x
                else:
                    val = event.data.positionStart.x + event.data.position.x
            if val >= 0:
                direction = f"{(click_id[1])[0:1]}p"
                move = f"p{(click_id[1])[2:4]}"
            else:
                direction = f"{(click_id[1])[0:1]}n"
                move = f"n{(click_id[1])[2:4]}"
            return (obj, direction, move, abs(val))
    else:
        # send camera movement for clickers
        if USERS[camname].gesturing:
            obj = scene.get_persisted_obj(object_id)
            # determine direction of 2d gesture in 3d
            if click_id[1][0] == "y":
                val = -(USERS[camname].position_last.y -
                        USERS[camname].position.y)
            elif click_id[1][0] == "x":
                val = -(USERS[camname].position_last.x -
                        USERS[camname].position.x)
            else:  # click_id[1][0] == "z":
                val = -(USERS[camname].position_last.z -
                        USERS[camname].position.z)
            if val >= 0:
                direction = f"{(click_id[1])[0:1]}p"
                move = f"p{(click_id[1])[2:4]}"
            else:
                direction = f"{(click_id[1])[0:1]}n"
                move = f"n{(click_id[1])[2:4]}"
            return (obj, direction, move, abs(val))

    # allow any user to change an object
    if event.type != EVT_MOUSEDOWN:
        return None, None, None, val
    if USERS[camname].mode != mode:
        return None, None, None, val
    obj = scene.get_persisted_obj(object_id)
    return (obj, direction, move, val)


def panel_callback(_scene, event, msg):
    camname, objid, drop = handle_panel_event(event)
    if not camname or not objid:
        return
    # ignore disabled
    if not USERS[camname].panel[objid].enabled:
        return

    update_controls(USERS[camname].target_id)
    mode = USERS[camname].panel[objid].mode
    btype = USERS[camname].panel[objid].type
    if btype == ButtonType.TOGGLE:
        USERS[camname].panel[objid].set_active(
            not USERS[camname].panel[objid].active)
    else:
        if mode == USERS[camname].mode:  # action cancel
            # button click is same, then goes off and NONE
            USERS[camname].panel[objid].set_active(False)
            USERS[camname].mode = Mode.NONE
            mode = Mode.NONE
        else:
            # if button goes on, last button must go off
            prev_objid = f"{camname}_button_{USERS[camname].mode.value}"
            if prev_objid in USERS[camname].panel:
                USERS[camname].panel[prev_objid].set_active(False)
            USERS[camname].panel[objid].set_active(True)
            USERS[camname].mode = mode
        USERS[camname].set_textleft(USERS[camname].mode)
        USERS[camname].set_textright("")
        USERS[camname].del_clipboard()
        # clear last dropdown
        for but in USERS[camname].dbuttons:
            USERS[camname].dbuttons[but].delete()
        USERS[camname].dbuttons.clear()

    active = USERS[camname].panel[objid].active
    # toggle buttons
    if mode == Mode.LOCK:
        USERS[camname].follow_lock = active
        # TODO: after lock ensure original ray keeps lock button in reticle
    elif mode == Mode.REDPILL:
        # TODO: migrate to shared-scene setting
        USERS[camname].redpill = active
        show_redpill_scene(active)
    elif mode == Mode.LAMP:
        USERS[camname].set_lamp(active)
    elif mode == Mode.SLIDER:
        USERS[camname].slider = active
    # active buttons
    if mode == Mode.CREATE:
        update_dropdown(camname, objid, mode, arblib.SHAPES, 2, shape_callback)
        USERS[camname].set_clipboard(
            callback=clipboard_callback,
            object_type=USERS[camname].target_style)
    elif mode == Mode.MODEL:
        update_dropdown(camname, objid, mode, MODELS, 2, model_callback)
        idx = MODELS.index(USERS[camname].target_style)
        url = MANIFEST[idx]['url_gltf']
        sca = MANIFEST[idx]['scale']
        USERS[camname].set_clipboard(
            callback=clipboard_callback, object_type=GLTF.object_type,
            scale=Scale(sca, sca, sca), url=url)
    elif mode == Mode.COLOR:
        update_dropdown(camname, objid, mode,
                        arblib.COLORS, -2, color_callback)
    elif mode == Mode.OCCLUDE:
        update_dropdown(camname, objid, mode, arblib.BOOLS, -2, gen_callback)
    elif mode == Mode.RENAME:
        USERS[camname].typetext = ""
        update_dropdown(camname, objid, mode, arblib.KEYS, -2, rename_callback)
        USERS[camname].set_textright(USERS[camname].typetext)
    elif mode == Mode.PARENT:
        USERS[camname].typetext = ""
        USERS[camname].set_textright(USERS[camname].typetext)
    elif mode == Mode.WALL:
        USERS[camname].set_clipboard(callback=wall_callback)
        USERS[camname].set_textright("Start: tap flush corner.")
    elif mode == Mode.NUDGE:
        update_dropdown(camname, objid, mode, arblib.METERS, 2, gen_callback)
        if USERS[camname].target_id:
            do_nudge_select(camname, USERS[camname].target_id)
    elif mode == Mode.SCALE:
        update_dropdown(camname, objid, mode, arblib.METERS, 2, gen_callback)
        if USERS[camname].target_id:
            do_scale_select(camname, USERS[camname].target_id)
    elif mode == Mode.STRETCH:
        update_dropdown(camname, objid, mode, arblib.METERS, 2, gen_callback)
        if USERS[camname].target_id:
            do_stretch_select(camname, USERS[camname].target_id)
    elif mode == Mode.ROTATE:
        update_dropdown(camname, objid, mode, arblib.DEGREES, 2, gen_callback)
        if USERS[camname].target_id:
            do_rotate_select(camname, USERS[camname].target_id)


def update_dropdown(camname, objid, mode, options, row, callback):
    # show new dropdown
    if USERS[camname].panel[objid].active:
        followname = USERS[camname].follow.object_id
        maxwidth = min(len(options), 10)
        drop_button_offset = -math.floor(maxwidth / 2)
        for i, option in enumerate(options):
            if mode is Mode.COLOR:
                bcolor = Color(option)
            else:
                bcolor = arblib.CLR_SELECT
            dbutton = arblib.Button(
                scene, camname, mode, (i % maxwidth) + drop_button_offset, row,
                label=option, parent=followname, color=bcolor, drop=option, callback=callback)
            USERS[camname].dbuttons[dbutton.button.object_id] = dbutton
            if (i + 1) % maxwidth == 0:  # next row
                if row < 0:
                    row -= 1
                else:
                    row += 1
        # make default selection
        if mode is Mode.COLOR:
            rcolor = Color(options[0])
        else:
            rcolor = arblib.CLR_HUDTEXT
        USERS[camname].set_textright(options[0], color=rcolor)
        USERS[camname].target_style = options[0]


def model_callback(_scene, event, msg):
    camname, objid, drop = handle_panel_event(event, dropdown=True)
    if not camname or not drop:
        return
    model = drop
    idx = MODELS.index(model)
    url = MANIFEST[idx]['url_gltf']
    sca = MANIFEST[idx]['scale']
    USERS[camname].set_clipboard(
        callback=clipboard_callback, object_type=GLTF.object_type,
        scale=Scale(sca, sca, sca), url=url)
    USERS[camname].set_textright(model)
    USERS[camname].target_style = model


def shape_callback(_scene, event, msg):
    camname, objid, drop = handle_panel_event(event, dropdown=True)
    if not camname or not drop:
        return
    shape = drop
    USERS[camname].set_clipboard(
        callback=clipboard_callback, object_type=shape)
    USERS[camname].set_textright(shape)
    USERS[camname].target_style = shape


def color_callback(_scene, event, msg):
    camname, objid, drop = handle_panel_event(event, dropdown=True)
    if not camname or not objid:
        return
    hcolor = drop
    color = Color(hcolor)
    USERS[camname].set_textright(hcolor, color=color)
    USERS[camname].target_style = hcolor


def gen_callback(_scene, event, msg):
    camname, objid, drop = handle_panel_event(event, dropdown=True)
    if not camname or not drop:
        return
    style = drop
    USERS[camname].set_textright(style)
    USERS[camname].target_style = style


def rename_callback(_scene, event, msg):
    camname, objid, drop = handle_panel_event(event, dropdown=True)
    if not camname or not drop:
        return
    key = drop
    USERS[camname].set_textright(key)
    USERS[camname].target_style = key
    if key == 'back':
        if len(USERS[camname].typetext) > 0:
            USERS[camname].typetext = USERS[camname].typetext[:-1]
    elif key == 'underline':
        USERS[camname].typetext = f"{USERS[camname].typetext}_"
    elif key == 'apriltag':  # special prefix, replace text with 'apriltag_'
        USERS[camname].typetext = 'apriltag_'
    else:
        USERS[camname].typetext = USERS[camname].typetext + key
    USERS[camname].set_textright(USERS[camname].typetext)


def show_redpill_scene(enabled):
    # any scene changes must not persist
    # show gridlines
    name = "grid_redpill"
    path = []
    glen = arblib.GRIDLEN
    y = arblib.FLOOR_Y
    for z in range(-glen, glen + 1):
        if (z % 2) == 0:
            path.append(Position(-glen, y, z))
            path.append(Position(glen, y, z))
        else:
            path.append(Position(glen, y, z))
            path.append(Position(-glen, y, z))
    for x in range(-glen, glen + 1):
        if (x % 2) == 0:
            path.append(Position(x, y, glen))
            path.append(Position(x, y, -glen))
        else:
            path.append(Position(x, y, -glen))
            path.append(Position(x, y, glen))

    if enabled:
        scene.add_object(ThickLine(
            object_id=name,
            path=path,
            color=arblib.CLR_GRID))
    else:
        arblib.delete_obj(scene, name)

    objs = scene.get_persisted_objs()
    for object_id in objs:
        obj = objs[object_id]
        # show occluded objects
        if "material-extras" in obj.data and "transparentOccluder" in obj.data["material-extras"]:
            name = "redpill_" + obj.object_id
            if enabled:
                object_type = "box"
                if "object_type" in obj.data:
                    object_type = obj.data.object_type
                position = Position()
                if "position" in obj.data:
                    position = obj.data.position
                rotation = Rotation()
                if "rotation" in obj.data:
                    rotation = obj.data.rotation
                scale = Scale()
                if "scale" in obj.data:
                    scale = obj.data.scale
                url = None
                if "url" in obj.data:
                    url = obj.data.url
                color = Color()
                if "material" in obj.data and "color" in obj.data.material:
                    color = obj.data.material.color
                scene.add_object(Object(
                    object_id=name,
                    object_type=object_type,
                    position=position,
                    rotation=rotation,
                    scale=scale,
                    clickable=True,
                    url=url,
                    material=Material(
                        color=color, transparent=True, opacity=0.5),
                ))
                print("Wrapping occlusion " + name)
            else:
                arblib.delete_obj(scene, name)


def do_rename(camname, old_id, new_id):
    if new_id == old_id:
        return
    obj = scene.get_persisted_obj(old_id)
    scene.add_object(
        Object(object_id=new_id, persist=obj.persist, **obj.data.__dict__))
    if new_id in scene.all_objects:
        USERS[camname].target_id = new_id
        print(f"Duplicating {old_id} to {new_id}")
        arblib.delete_obj(scene, old_id)


def show_redpill_obj(camname, object_id):
    # any scene changes must not persist
    obj = scene.get_persisted_obj(object_id)
    # enable mouse enter/leave pos/rot/scale
    position = Position()
    if "position" in obj.data:
        position = obj.data.position
    rotation = Rotation()
    if "rotation" in obj.data:
        rotation = obj.data.rotation
    scale = Scale()
    if "scale" in obj.data:
        scale = obj.data.scale
    USERS[camname].set_textstatus(
        " ".join([f"{object_id}",
                  f"p({position.x},{position.y},{position.z})",
                  f"r({rotation.x},{rotation.y},{rotation.z},{rotation.w})",
                  f"s({scale.x},{scale.y},{scale.z})"]))


def do_move_select(camname, object_id):
    obj = scene.get_persisted_obj(object_id)
    USERS[camname].target_id = object_id
    object_type = "box"
    if "object_type" in obj.data:
        object_type = obj.data.object_type
    scale = Scale()
    if "scale" in obj.data:
        scale = obj.data.scale
    color = Color()
    if "material" in obj.data and "color" in obj.data.material:
        color = obj.data.material.color
    url = None
    if "url" in obj.data:
        url = obj.data.url
    USERS[camname].set_clipboard(
        callback=clipboard_callback,
        object_type=object_type,
        scale=scale,
        color=color,
        url=url,
    )


def update_controls(objid):
    if objid not in CONTROLS.keys():
        CONTROLS[objid] = {}
    for ctrl in CONTROLS[objid]:
        scene.delete_object(CONTROLS[objid][ctrl])
    CONTROLS[objid].clear()


def do_nudge_select(camname, objid, position=None):
    color = arblib.CLR_NUDGE
    delim = f"_{Mode.NUDGE.value}_"
    callback = nudgeline_callback
    obj = scene.get_persisted_obj(objid)
    if not position:
        position = Position()
        if "position" in obj.data:
            position = obj.data.position
    xl, yl, zl = get_clicklines_len(obj)
    # nudge object + or - on 3 axis
    root = make_clickroot(objid, position, delim, move=True)
    make_clickline("x", xl, objid, position, delim, color,
                   callback, move=True, parent=root)
    make_clickline("y", yl, objid, position, delim, color,
                   callback, move=True, parent=root)
    make_clickline("z", zl, objid, position, delim, color,
                   callback, move=True, parent=root)
    # TODO: restore make_followspot(objid, position, delim, color, move=True)
    pos = Position(round(position.x, 3), round(
        position.y, 3), round(position.z, 3))
    USERS[camname].set_textright(
        f"{USERS[camname].target_style} p({pos.x},{pos.y},{pos.z})")


def do_scale_select(camname, objid, scale=None):
    color = arblib.CLR_SCALE
    delim = f"_{Mode.SCALE.value}_"
    callback = scaleline_callback
    obj = scene.get_persisted_obj(objid)
    position = Position()
    if "position" in obj.data:
        position = obj.data.position
    if not scale:
        scale = Scale()
        if "scale" in obj.data:
            scale = obj.data.scale
    xl, yl, zl = get_clicklines_len(obj)
    # scale entire object + or - on all axis
    root = make_clickroot(objid, position, delim, move=True)
    make_clickline("x", xl, objid, position, delim, color,
                   callback, move=True, parent=root)
    # TODO: restore make_followspot(objid, position, delim, color)
    sca = Scale(round(scale.x, 3), round(scale.y, 3), round(scale.z, 3))
    USERS[camname].set_textright(
        f"{USERS[camname].target_style} s({sca.x},{sca.y},{sca.z})")


def do_stretch_select(camname, objid, scale=None):
    color = arblib.CLR_STRETCH
    delim = f"_{Mode.STRETCH.value}_"
    callback = stretchline_callback
    obj = scene.get_persisted_obj(objid)
    position = Position()
    if "position" in obj.data:
        position = obj.data.position
    if not scale:
        object_type = "box"
        if "object_type" in obj.data:
            object_type = obj.data.object_type
        rotation = Rotation()
        if "rotation" in obj.data:
            rotation = obj.data.rotation
        scale = Scale()
        if "scale" in obj.data:
            scale = obj.data.scale
        # TODO: scale too unpredictable, modify
        if object_type == GLTF.object_type:
            return
        # TODO: scale too unpredictable, modify
        if rotation.quaternion.__dict__ != Rotation(x=0, y=0, z=0, w=1).quaternion.__dict__:
            return
    xl, yl, zl = get_clicklines_len(obj)
    # scale and reposition on one of 6 sides
    root = make_clickroot(objid, position, delim, move=True)
    make_clickline("x", xl, objid, position, delim, color,
                   callback, move=True, parent=root)
    make_clickline("x", -xl, objid, position, delim,
                   color, callback, move=True, parent=root)
    make_clickline("y", yl, objid, position, delim, color,
                   callback, move=True, parent=root)
    make_clickline("y", -yl, objid, position, delim,
                   color, callback, move=True, parent=root)
    make_clickline("z", zl, objid, position, delim, color,
                   callback, move=True, parent=root)
    make_clickline("z", -zl, objid, position, delim,
                   color, callback, move=True, parent=root)
    # TODO: restore make_followspot(objid, position, delim, color)
    sca = Scale(round(scale.x, 3), round(scale.y, 3), round(scale.z, 3))
    USERS[camname].set_textright(
        f"{USERS[camname].target_style} s({sca.x},{sca.y},{sca.z})")


def do_rotate_select(camname, objid, rotation=None):
    color = arblib.CLR_ROTATE
    delim = f"_{Mode.ROTATE.value}_"
    callback = rotateline_callback
    obj = scene.get_persisted_obj(objid)
    position = Position()
    if "position" in obj.data:
        position = obj.data.position
    if not rotation:
        rotation = Rotation()
        if "rotation" in obj.data:
            rotation = obj.data.rotation
    xl, yl, zl = get_clicklines_len(obj)
    # rotate object + or - on 3 axis, plus show original axis as after
    # effect
    root = make_clickroot(objid, position, delim)
    ghost = make_clickroot(objid, position, delim,
                           rotation=rotation, move=True)
    make_clickline("x", xl, objid, position, delim, color,
                   callback, ghost=ghost, parent=root)
    make_clickline("y", yl, objid, position, delim, color,
                   callback, ghost=ghost, parent=root)
    make_clickline("z", zl, objid, position, delim, color,
                   callback, ghost=ghost, parent=root)
    # TODO: restore make_followspot(objid, position, delim, color)
    try:
        rote = arblib.rotation_quat2euler(
            (rotation.x, rotation.y, rotation.z, rotation.w))
    except ValueError as error:
        print(f"Rotation error: {error}")
        return
    euler = (round(rote[0], 1), round(rote[1], 1), round(rote[2], 1))
    USERS[camname].set_textright(
        f"{USERS[camname].target_style}d r({euler[0]},{euler[1]},{euler[2]})")


def get_clicklines_len(obj):
    object_type = "box"
    if "object_type" in obj.data:
        object_type = obj.data.object_type
    scale = Scale()
    if "scale" in obj.data:
        scale = obj.data.scale
    if object_type == "gltf-model":
        # TODO: if we can get the gltf size (not scale), we can make accurate clicklines
        scale = Scale(0.1, 0.1, 0.1)
        line_extension = arblib.CLICKLINE_LEN_MOD
    else:
        line_extension = arblib.CLICKLINE_LEN_OBJ
    xl = scale.x + line_extension
    yl = scale.y + line_extension
    zl = scale.z + line_extension
    print(xl, yl, zl)
    return xl, yl, zl


def make_followspot(object_id, position, delim, color, parent, move=False):
    name = f"{object_id}{delim}spot"
    if name not in CONTROLS[object_id]:
        CONTROLS[object_id][name] = Circle(  # follow spot on ground
            object_id=name,
            scale=Scale(0.1, 0.1, 0.1),
            # TODO: restore ttl=arblib.TTL_TEMP,
            position=Position(position.x, arblib.FLOOR_Y, position.z),
            rotation=Rotation(-0.7, 0, 0, 0.7),
            parent=parent,
            material=Material(
                color=color,
                transparent=True,
                opacity=0.4,
                shader="flat"),
        )
        scene.add_object(CONTROLS[object_id][name])
    elif move:
        scene.update_object(CONTROLS[object_id][name], position=position)


def regline(object_id, axis, direction, delim, suffix, start,
            end, line_width, move, color, parent):
    line_width = line_width/SCL_CLICK
    end = Position(x=(end.x - start.x)/SCL_CLICK,
                   y=(end.y - start.y)/SCL_CLICK,
                   z=(end.z - start.z)/SCL_CLICK)
    name = f"{object_id}{delim}{axis}{direction}_{suffix}"
    if name not in CONTROLS[object_id]:
        CONTROLS[object_id][name] = Line(
            object_id=name,
            color=color,
            # TODO: restore ttl=arblib.TTL_TEMP,
            parent=parent,
            start=start,
            end=end)
        scene.add_object(CONTROLS[object_id][name])
    elif move:
        scene.update_object(CONTROLS[object_id][name], start=start, end=end)


def boxline(object_id, axis, direction, delim, suffix, start,
            end, line_width, move, color, parent):
    line_width = line_width/SCL_CLICK
    end = Position(x=(end.x - start.x)/SCL_CLICK,
                   y=(end.y - start.y)/SCL_CLICK,
                   z=(end.z - start.z)/SCL_CLICK)
    if start.y == end.y and start.z == end.z:
        scale = Scale(x=abs(start.x - end.x), y=line_width, z=line_width)
    elif start.x == end.x and start.z == end.z:
        scale = Scale(x=line_width, y=abs(start.y - end.y), z=line_width)
    elif start.x == end.x and start.y == end.y:
        scale = Scale(x=line_width, y=line_width, z=abs(start.z - end.z))
    name = f"{object_id}{delim}{axis}{direction}_{suffix}"
    position = Position(statistics.median([start.x, end.x]),
                        statistics.median([start.y, end.y]),
                        statistics.median([start.z, end.z]))
    if name not in CONTROLS[object_id]:
        CONTROLS[object_id][name] = Box(
            object_id=name,
            # TODO: restore ttl=arblib.TTL_TEMP,
            parent=parent,
            scale=scale,
            position=position,
            material=Material(
                color=color,
                transparent=True,
                opacity=0.4,
                shader="flat"),
        )
        scene.add_object(CONTROLS[object_id][name])
    elif move:
        scene.update_object(CONTROLS[object_id][name],
                            position=position, scale=scale)


def dir_clickers(object_id, axis, direction, delim, position,
                 color, cones, callback, move, parent):
    position = Position(x=position.x/SCL_CLICK,
                        y=position.y/SCL_CLICK,
                        z=position.z/SCL_CLICK)
    loc = Position(x=position.x/SCL_CLICK,
                   y=position.y/SCL_CLICK,
                   z=position.z/SCL_CLICK)
    npos = 0.1/SCL_CLICK
    if direction == "p":
        npos = -0.1/SCL_CLICK
    if axis == "x":
        loc = Position(x=position.x + npos, y=position.y, z=position.z)
    elif axis == "y":
        loc = Position(x=position.x, y=position.y + npos, z=position.z)
    elif axis == "z":
        loc = Position(x=position.x, y=position.y, z=position.z + npos)
    name_pos = f"{object_id}{delim}{axis}p_{direction}"
    name_neg = f"{object_id}{delim}{axis}n_{direction}"
    if name_pos not in CONTROLS[object_id]:
        CONTROLS[object_id][name_pos] = Cone(   # click object positive
            object_id=name_pos,
            clickable=True,
            position=position,
            rotation=cones[axis + direction][0],
            scale=Scale(0.05/SCL_CLICK, 0.09/SCL_CLICK, 0.05/SCL_CLICK),
            material=Material(color=color, transparent=True,
                              opacity=arblib.OPC_CLINE),
            # TODO: restore ttl=arblib.TTL_TEMP,
            parent=parent,
            evt_handler=callback)
        scene.add_object(CONTROLS[object_id][name_pos])
    elif move:
        scene.update_object(CONTROLS[object_id][name_pos], position=position)
    if name_neg not in CONTROLS[object_id]:
        CONTROLS[object_id][name_neg] = Cone(  # click object negative
            object_id=name_neg,
            clickable=True,
            position=loc,
            rotation=cones[axis + direction][1],
            scale=Scale(0.05/SCL_CLICK, 0.09/SCL_CLICK, 0.05/SCL_CLICK),
            material=Material(color=color, transparent=True,
                              opacity=arblib.OPC_CLINE),
            # TODO: restore ttl=arblib.TTL_TEMP,
            parent=parent,
            evt_handler=callback)
        scene.add_object(CONTROLS[object_id][name_neg])
    elif move:
        scene.update_object(CONTROLS[object_id][name_neg], position=loc)


def make_clickline(axis, linelen, objid, start, delim,
                   color, callback, ghost=None, parent=None, move=False):
    if objid not in CONTROLS.keys():
        CONTROLS[objid] = {}
    endx = endy = endz = 0
    direction = "p"
    if linelen < 0:
        direction = "n"
    if axis == "x":
        endx = linelen
    elif axis == "y":
        endy = linelen
    elif axis == "z":
        endz = linelen
    start = Position(0, 0, 0)
    end = Position(x=start.x + endx, y=start.y + endy, z=start.z + endz)
    boxline(  # reference line
        object_id=objid, axis=axis, direction=direction, delim=delim,
        suffix="line", color=color, start=start, end=end, line_width=0.005, move=move,
        parent=parent)
    if ghost:
        boxline(  # ghostline aligns to parent rotation
            object_id=objid, axis=axis, direction=direction, delim=delim,
            suffix="ghost", color=(255, 255, 255), start=start, end=end, line_width=0.005,
            move=move, parent=ghost)
    if ghost:
        cones = arblib.ROTATE_CONES
    else:
        cones = arblib.DIRECT_CONES
    dir_clickers(  # click objects
        object_id=objid, axis=axis, direction=direction, delim=delim, position=end,
        color=color, cones=cones, callback=callback, move=move, parent=parent)


def make_clickroot(objid, position, delim, rotation=None, move=False):
    if objid not in CONTROLS.keys():
        CONTROLS[objid] = {}
    name = f"{objid}{delim}clickroot"
    if rotation:
        name += "_rotated"
    else:
        rotation = Rotation(0, 0, 0, 1)
    if name not in CONTROLS[objid]:
        CONTROLS[objid][name] = Box(
            object_id=name,
            material=Material(transparent=True, opacity=0),
            position=position,
            scale=Scale(SCL_CLICK, SCL_CLICK, SCL_CLICK),
            rotation=rotation,
        )
        scene.add_object(CONTROLS[objid][name])
    elif move:
        scene.update_object(CONTROLS[objid][name],
                            position=position, rotation=rotation)
    return name


def do_move_relocate(camname, newposition):
    arblib.move_obj(scene, USERS[camname].target_id, newposition)
    USERS[camname].del_clipboard()


def incr_pos(coord, incr):
    div = round(coord / incr)
    res = (math.ceil(div) * incr) + incr
    return float('{0:g}'.format(res))


def incr_neg(coord, incr):
    div = round(coord / incr)
    res = (math.floor(div) * incr) - incr
    return float('{0:g}'.format(res))


def meters_increment(meters_style):
    if meters_style == "mm":
        return 0.001
    elif meters_style == "cm":
        return 0.01
    elif meters_style == "dm":
        return 0.1
    elif meters_style == "m":
        return 1.0


def nudgeline_callback(_scene, event, msg):
    obj, direction, move, val = handle_clickline_event(event, Mode.NUDGE)
    if not obj or not direction or "position" not in obj.data:
        return
    nudged = loc = obj.data.position
    if val == 0:
        inc = meters_increment(USERS[event.data.source].target_style)
    else:
        inc = val
    if direction == "xp":
        nudged = Position(x=incr_pos(loc.x, inc), y=loc.y, z=loc.z)
    elif direction == "xn":
        nudged = Position(x=incr_neg(loc.x, inc), y=loc.y, z=loc.z)
    elif direction == "yp":
        nudged = Position(x=loc.x, y=incr_pos(loc.y, inc), z=loc.z)
    elif direction == "yn":
        nudged = Position(x=loc.x, y=incr_neg(loc.y, inc), z=loc.z)
    elif direction == "zp":
        nudged = Position(x=loc.x, y=loc.y, z=incr_pos(loc.z, inc))
    elif direction == "zn":
        nudged = Position(x=loc.x, y=loc.y, z=incr_neg(loc.z, inc))
    arblib.move_obj(scene, obj.object_id, nudged)
    print(f"{str(obj.data.position)} to {str(nudged)}")
    # always redraw nudgelines
    do_nudge_select(event.data.source, obj.object_id, position=nudged)


def scaleline_callback(_scene, event, msg):
    obj, direction, move, val = handle_clickline_event(event, Mode.SCALE)
    if not obj or not direction or "scale" not in obj.data:
        return
    scaled = sca = obj.data.scale
    if val == 0:
        inc = meters_increment(USERS[event.data.source].target_style)
    else:
        inc = val
    if direction == "xp":
        scaled = Scale(x=incr_pos(sca.x, inc), y=incr_pos(
            sca.y, inc), z=incr_pos(sca.z, inc))
    elif direction == "xn":
        scaled = Scale(x=incr_neg(sca.x, inc), y=incr_neg(
            sca.y, inc), z=incr_neg(sca.z, inc))
    if scaled.x <= 0 or scaled.y <= 0 or scaled.z <= 0:
        return
    arblib.scale_obj(scene, obj.object_id, scaled)
    print(f"{str(obj.data.scale)} to {str(scaled)}")
    do_scale_select(event.data.source, obj.object_id, scale=scaled)


def stretchline_callback(_scene, event, msg):
    obj, direction, move, val = handle_clickline_event(event, Mode.STRETCH)
    if not obj or not direction or not move or "scale" not in obj.data or "position" not in obj.data:
        return
    scaled = sca = obj.data.scale
    moved = loc = obj.data.position
    if val == 0:
        inc = meters_increment(USERS[event.data.source].target_style)
    else:
        inc = val
    if direction == "xp":
        scaled = Scale(x=incr_pos(sca.x, inc), y=sca.y, z=sca.z)
        moved = Position(x=recenter(
            scaled.x, sca.x, loc.x, move), y=loc.y, z=loc.z)
    elif direction == "xn":
        scaled = Scale(x=incr_neg(sca.x, inc), y=sca.y, z=sca.z)
        moved = Position(x=recenter(
            scaled.x, sca.x, loc.x, move), y=loc.y, z=loc.z)
    elif direction == "yp":
        scaled = Scale(x=sca.x, y=incr_pos(sca.y, inc), z=sca.z)
        moved = Position(x=loc.x, y=recenter(
            scaled.y, sca.y, loc.y, move), z=loc.z)
    elif direction == "yn":
        scaled = Scale(x=sca.x, y=incr_neg(sca.y, inc), z=sca.z)
        moved = Position(x=loc.x, y=recenter(
            scaled.y, sca.y, loc.y, move), z=loc.z)
    elif direction == "zp":
        scaled = Scale(x=sca.x, y=sca.y, z=incr_pos(sca.z, inc))
        moved = Position(x=loc.x, y=loc.y, z=recenter(
            scaled.z, sca.z, loc.z, move))
    elif direction == "zn":
        scaled = Scale(x=sca.x, y=sca.y, z=incr_neg(sca.z, inc))
        moved = Position(x=loc.x, y=loc.y, z=recenter(
            scaled.z, sca.z, loc.z, move))
    if scaled.x <= 0 or scaled.y <= 0 or scaled.z <= 0:
        return
    arblib.stretch_obj(scene, obj.object_id,
                       scale=scaled, position=moved)
    print(f"{str(obj.data.scale)} to {str(scaled)}")
    do_stretch_select(event.data.source, obj.object_id, scale=scaled)


def rotateline_callback(_scene, event, msg):
    obj, direction, move, val = handle_clickline_event(event, Mode.ROTATE)
    if not obj or not direction or "rotation" not in obj.data:
        return
    rotated = rot = obj.data.rotation
    inc = float(USERS[event.data.source].target_style)
    try:
        rot = arblib.rotation_quat2euler((rot.x, rot.y, rot.z, rot.w))
    except ValueError as error:
        print(f"Rotation error: {error}")
        return
    rot = (round(rot[0]), round(rot[1]), round(rot[2]))
    if direction == "xp":
        rotated = (incr_pos(rot[0], inc), rot[1], rot[2])
    elif direction == "xn":
        rotated = (incr_neg(rot[0], inc), rot[1], rot[2])
    elif direction == "yp":
        rotated = (rot[0], incr_pos(rot[1], inc), rot[2])
    elif direction == "yn":
        rotated = (rot[0], incr_neg(rot[1], inc), rot[2])
    elif direction == "zp":
        rotated = (rot[0], rot[1], incr_pos(rot[2], inc))
    elif direction == "zn":
        rotated = (rot[0], rot[1], incr_neg(rot[2], inc))
    if abs(rotated[0]) > 180 or abs(rotated[1]) > 180 or abs(rotated[2]) > 180:
        return
    try:
        rotated = arblib.rotation_euler2quat(rotated)
    except ValueError as error:
        print(f"Rotation error: {error}")
        return
    rotated = Rotation(x=rotated[0], y=rotated[1], z=rotated[2], w=rotated[3])
    arblib.rotate_obj(scene, obj.object_id, rotated)
    print(f"{str(obj.data.rotation)} to {str(rotated)}")
    do_rotate_select(event.data.source, obj.object_id, rotation=rotated)


def recenter(scaled, sca, loc, move):
    if move == "p_p" or move == "n_n":
        return loc + (abs(sca - scaled) / 2)
    else:
        return loc - (abs(sca - scaled) / 2)


def create_obj(camname, clipboard, position):
    randstr = str(random.randrange(0, 1000000))
    # make a copy of static object in place
    new_obj = Object(
        persist=True,
        object_id=f"{clipboard.data.object_type}_{randstr}",
        object_type=clipboard.data.object_type,
        position=position,
        # undo clipboard rotation for visibility
        rotation=Rotation(0, 0, 0, 1),
        scale=clipboard.data.scale,
        material=Material(color=clipboard.data.material.color,
                          transparent=False),
        url=clipboard.data.url,
        clickable=True)
    scene.add_object(new_obj)
    USERS[camname].target_id = new_obj.object_id
    print("Created " + new_obj.object_id)


def clipboard_callback(_scene, event, msg):
    camname = handle_clip_event(event)
    if not camname:
        return
    position = event.data.position
    if USERS[camname].mode == Mode.CREATE or USERS[camname].mode == Mode.MODEL:
        create_obj(camname, USERS[camname].get_clipboard(), position)
    elif USERS[camname].mode == Mode.MOVE:
        do_move_relocate(camname, position)


def wall_callback(_scene, event, msg):
    camname = handle_clip_event(event)
    if not camname:
        return
    if not USERS[camname].wloc_start:
        do_wall_start(camname)
        USERS[camname].set_textright("End: tap opposing corner.")
    else:
        do_wall_end(camname)
        make_wall(camname)
        USERS[camname].wloc_start = USERS[camname].wloc_end = None  # reset
        USERS[camname].set_textright("Start: tap flush corner.")


def do_wall_start(camname):
    # start (red)
    USERS[camname].wloc_start = USERS[camname].position
    USERS[camname].wrot_start = USERS[camname].rotation
    scene.add_object(arblib.temp_loc_marker(
        USERS[camname].wloc_start, Color(255, 0, 0)))
    scene.add_object(arblib.temp_rot_marker(USERS[camname].wloc_start,
                                            USERS[camname].wrot_start))


def do_wall_end(camname):
    # end (green)
    USERS[camname].wloc_end = USERS[camname].position
    USERS[camname].wrot_end = USERS[camname].rotation
    scene.add_object(arblib.temp_loc_marker(
        USERS[camname].wloc_end, Color(0, 255, 0)))
    scene.add_object(arblib.temp_rot_marker(
        USERS[camname].wloc_end, USERS[camname].wrot_end))


def make_wall(camname):
    # Wall theory: capture two poses and use them to place a wall object.
    # Also assumes first corner easier to capture accurate rotation than last.
    # Click 1: Capture the position and rotation.
    # Click 2: Capture the position only.
    sloc = USERS[camname].wloc_start
    eloc = USERS[camname].wloc_end
    srot = USERS[camname].wrot_start
    erot = USERS[camname].wrot_end
    print(f"S POS {str(sloc)}")
    print(f"E POS {str(eloc)}")
    # center point (blue)
    locx = statistics.median([sloc.x, eloc.x])
    locy = statistics.median([sloc.y, eloc.y])
    locz = statistics.median([sloc.z, eloc.z])
    pos = Position(locx, locy, locz)
    scene.add_object(arblib.temp_loc_marker(pos, Color(0, 0, 255)))
    print(f"wall position {str(pos)}")
    # rotation
    print(f"S ROT {str(srot)}")
    print(f"E ROT {str(erot)}")
    rotx = arblib.probable_quat(srot.x)
    roty = arblib.probable_quat(srot.y)
    rotz = arblib.probable_quat(srot.z)
    rotw = arblib.probable_quat(srot.w)
    rot = Rotation(rotx, roty, rotz, rotw)
    gaze = (rotx, roty, rotz, rotw)
    scene.add_object(arblib.temp_rot_marker(pos, rot))
    print(f"wall rotation {str(rot)}")
    # which axis to use for wall? use camera gaze
    # TODO: rotation still off
    if gaze in arblib.GAZES[0]:
        height = abs(sloc.y - eloc.y)
        width = abs(sloc.x - eloc.x)
    elif gaze in arblib.GAZES[1]:
        height = abs(sloc.y - eloc.y)
        width = abs(sloc.z - eloc.z)
    elif gaze in arblib.GAZES[2]:
        height = abs(sloc.z - eloc.z)
        width = abs(sloc.x - eloc.x)
    else:
        # TODO: (placeholder) add direction and hypotenuse
        height = abs(sloc.y - eloc.y)
        width = abs(sloc.x - eloc.x)
        print(f"Non-axis parallel rotation: {str(rot)}")
    # scale
    scax = width
    scay = height
    scaz = arblib.WALL_WIDTH
    sca = Scale(scax, scay, scaz)
    print(f"wall scale {str(sca)}")
    # make wall
    randstr = str(random.randrange(0, 1000000))
    new_wall = Box(
        persist=True,
        clickable=True,
        object_id=f"wall_{randstr}",
        position=pos,
        rotation=rot,
        scale=sca,
        material=Material(color=Color(200, 200, 200),
                          transparent=True, opacity=0.5),
    )
    scene.add_object(new_wall)
    USERS[camname].target_id = new_wall.object_id
    print(f"Created {new_wall.object_id} r{str(rot)} s{str(sca)}")
    # TODO: remove wall opacity in final wall feature
    # TODO: push wall front side flush with markers (position-(wall/2))


def scene_callback(_scene, event, msg):
    # This is the MQTT message callback function for the scene
    object_id = action = msg_type = object_type = None
    if "object_id" in msg:
        object_id = msg["object_id"]
    if "action" in msg:
        action = msg["action"]
    if "type" in msg:
        msg_type = msg["type"]
    if "data" in msg and "object_type" in msg["data"]:
        object_type = msg["data"]["object_type"]
    # print(f'{object_type} {action} {msg_type} {object_id}')

    if object_type == "camera":
        # camera updates define users present
        camname = object_id
        if camname not in USERS:
            USERS[camname] = arblib.User(scene, camname, panel_callback)

        # save camera's attitude in the world
        USERS[camname].position_last = USERS[camname].position
        USERS[camname].rotation_last = USERS[camname].rotation
        USERS[camname].position = Position(msg["data"]["position"]["x"],
                                           msg["data"]["position"]["y"],
                                           msg["data"]["position"]["z"])
        USERS[camname].rotation = Rotation(msg["data"]["rotation"]["x"],
                                           msg["data"]["rotation"]["y"],
                                           msg["data"]["rotation"]["z"],
                                           msg["data"]["rotation"]["w"])

        rx = msg["data"]["rotation"]["x"]
        ry = msg["data"]["rotation"]["y"]

        # floating controller
        if not USERS[camname].follow_lock:
            ty = -(ry + USERS[camname].locky) / 0.7 * math.pi / 2
            tx = -(rx + USERS[camname].lockx) / 0.7 * math.pi / 2
            px = arblib.PANEL_RADIUS * -math.cos(ty)
            py = arblib.PANEL_RADIUS * math.sin(tx)
            pz = arblib.PANEL_RADIUS * math.sin(ty)
            scene.update_object(USERS[camname].follow,
                                position=Position(px, py, pz))
        # else: # TODO: panel lock position drop is inaccurate
            # users[camname].lockx = rx + arblib.LOCK_XOFF
            # users[camname].locky = -(ry * math.pi) - arblib.LOCK_YOFF

        # handle gesturing two-finger touch as clickline camera match-moves
        if USERS[camname].gesturing and not USERS[camname].slider:
            event["data"]["source"] = camname
            if USERS[camname].mode == Mode.NUDGE:
                nudgeline_callback(_scene, event, msg)
            elif USERS[camname].mode == Mode.ROTATE:
                rotateline_callback(_scene, event, msg)
            elif USERS[camname].mode == Mode.SCALE:
                scaleline_callback(_scene, event, msg)
            elif USERS[camname].mode == Mode.STRETCH:
                stretchline_callback(_scene, event, msg)

    # mouse event
    elif action == "clientEvent":
        object_id = msg["object_id"]
        # camera updates define users present
        camname = msg["data"]["source"]
        if camname not in USERS:
            USERS[camname] = arblib.User(scene, camname, panel_callback)

        # show objects with events
        if msg_type == EVT_MOUSEENTER:
            if USERS[camname].redpill:
                show_redpill_obj(camname, object_id)
            else:
                USERS[camname].set_textstatus(object_id)
        elif msg_type == EVT_MOUSELEAVE:
            USERS[camname].set_textstatus("")

        # handle click
        elif msg_type == EVT_MOUSEDOWN:
            # clicked on persisted object to modify
            update_controls(USERS[camname].target_id)
            USERS[camname].target_id = object_id  # always update
            if USERS[camname].mode == Mode.DELETE:
                arblib.delete_obj(scene, object_id)
            elif USERS[camname].mode == Mode.MOVE:
                do_move_select(camname, object_id)
            elif USERS[camname].mode == Mode.NUDGE:
                do_nudge_select(camname, object_id)
            elif USERS[camname].mode == Mode.SCALE:
                do_scale_select(camname, object_id)
            elif USERS[camname].mode == Mode.STRETCH:
                do_stretch_select(camname, object_id)
            elif USERS[camname].mode == Mode.ROTATE:
                do_rotate_select(camname, object_id)
            elif USERS[camname].mode == Mode.COLOR:
                arblib.color_obj(scene, object_id,
                                 Color(USERS[camname].target_style))
            elif USERS[camname].mode == Mode.OCCLUDE:
                arblib.occlude_obj(scene, object_id,
                                   USERS[camname].target_style)
            elif USERS[camname].mode == Mode.RENAME or USERS[camname].mode == Mode.PARENT:
                if len(USERS[camname].typetext) > 0:  # edits already made
                    new_id = USERS[camname].typetext
                    USERS[camname].typetext = ""
                    if USERS[camname].mode == Mode.PARENT:
                        arblib.parent_obj(scene, object_id, new_id)
                    else:
                        do_rename(camname, object_id, new_id)
                else:  # no edits yet, load previous name to change
                    USERS[camname].typetext = object_id
                USERS[camname].set_textright(USERS[camname].typetext)

        # handle two-finger touch as clickline sliders
        elif msg_type == "twofingerstart" or msg_type == "twofingermove" or msg_type == "twofingerend":
            if USERS[camname].mode == Mode.NUDGE:
                nudgeline_callback(_scene, event, msg)
            elif USERS[camname].mode == Mode.ROTATE:
                rotateline_callback(_scene, event, msg)
            elif USERS[camname].mode == Mode.SCALE:
                scaleline_callback(_scene, event, msg)
            elif USERS[camname].mode == Mode.STRETCH:
                stretchline_callback(_scene, event, msg)

        # handle three-finger touch as toggle for clickline modes
        elif msg_type == "threefingerstart":
            if USERS[camname].mode == Mode.NONE:
                buttonname = Mode.ROTATE
            elif USERS[camname].mode == Mode.ROTATE:
                buttonname = Mode.NUDGE
            elif USERS[camname].mode == Mode.NUDGE:
                buttonname = Mode.SCALE
            elif USERS[camname].mode == Mode.SCALE:
                buttonname = Mode.STRETCH
            else:
                buttonname = USERS[camname].mode  # collapse
            event = Event(  # convert to panel click
                object_id=f"{camname}_button_{buttonname.value}",
                action="clientEvent",
                type=EVT_MOUSEDOWN,
                data={"source": camname})
            panel_callback(_scene, event, msg)


def end_program_callback(_scene):
    for camname in USERS:
        USERS[camname].delete()
    show_redpill_scene(False)
    # TODO: remove origin marker
    for objid in CONTROLS:
        for ctrl in CONTROLS[objid]:
            _scene.delete_object(CONTROLS[objid][ctrl])


# parse args and wait for events
init_args()
random.seed()
kwargs = {}
if PORT:
    kwargs["port"] = PORT
if NAMESPACE:
    kwargs["namespace"] = NAMESPACE
if DEBUG:
    kwargs["debug"] = DEBUG
scene = Scene(
    host=BROKER,
    realm=REALM,
    scene=SCENE,
    on_msg_callback=scene_callback,
    end_program_callback=end_program_callback,
    **kwargs)
scene.run_tasks()
