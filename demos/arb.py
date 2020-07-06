# arb.py
#
# AR Builder
# Pass in args for scene name and/or broker and realm.

# pylint: disable=missing-docstring

# TODO: stretch (6Dof)
# TODO: highlight mouseenter to avoid click
# TODO: fix follow unlock position relative, not default
# TODO: handle click-listener objects with 1.1 x scale shield?
# TODO: add easy doc overlay for each button operation
# TODO: models in clipboard origin may be outside reticle

# TODO: document slack suggestions into issues for tracking

import argparse
import json
import math
import random
import statistics

import arblib
from arblib import ButtonType, Mode
import arena

BROKER = "oz.andrew.cmu.edu"
REALM = "realm"
SCENE = ""  # no default scene, arb works on any scene
MANIFEST = arblib.DEF_MANIFEST
MODELS = []
USERS = {}  # dictionary of user instances


def init_args():
    global BROKER, REALM, SCENE, MODELS, MANIFEST
    parser = argparse.ArgumentParser(description='ARENA AR Builder.')
    parser.add_argument(
        'scene', type=str, help='ARENA scene name')
    parser.add_argument(
        '-b', '--broker', type=str, help='MQTT message broker hostname', default=BROKER)
    parser.add_argument(
        '-r', '--realm', type=str, help='ARENA realm name', default=REALM)
    parser.add_argument(
        '-m', '--models', type=str, help='JSON GLTF manifest')
    args = parser.parse_args()
    print(args)
    SCENE = args.scene
    if args.broker is not None:
        BROKER = args.broker
    if args.realm is not None:
        REALM = args.realm
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


def panel_callback(event=None):
    if event.event_type != arena.EventType.mousedown:
        return
    obj = event.object_id.split("_")
    camname = event.source
    owner = obj[2] + "_" + obj[3] + "_" + obj[4]  # callback owner in object_id
    if owner != camname:
        return  # only owner may activate
    objid = event.object_id

    # ignore disabled
    if not USERS[camname].panel[objid].enabled:
        return

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
        else:
            # if button goes on, last button must go off
            prev_objid = "button_" + USERS[camname].mode.value + "_" + camname
            if prev_objid in USERS[camname].panel:
                USERS[camname].panel[prev_objid].set_active(False)
            USERS[camname].panel[objid].set_active(True)
            USERS[camname].mode = mode
        USERS[camname].set_textleft(USERS[camname].mode)
        USERS[camname].set_textright("")
        USERS[camname].target_id = None
        USERS[camname].clipboard.delete()
        # clear last dropdown
        for but in USERS[camname].dbuttons:
            but.delete()
        USERS[camname].dbuttons.clear()

    active = USERS[camname].panel[objid].active
    # toggle buttons
    if mode == Mode.LOCK:
        USERS[camname].follow_lock = active
        # TODO: after lock ensure original ray keeps lock button in reticle
    elif mode == Mode.REDPILL:
        USERS[camname].redpill = active
        show_redpill_scene(active)
    elif mode == Mode.LAMP:
        USERS[camname].set_lamp(active)
    # active buttons
    if mode == Mode.CREATE:
        update_dropdown(camname, objid, mode, arblib.SHAPES, 2, shape_callback)
        USERS[camname].clipboard = arblib.set_clipboard(
            camname, callback=clipboard_callback,
            obj_type=arena.Shape(USERS[camname].target_style))
    elif mode == Mode.MODEL:
        update_dropdown(camname, objid, mode, MODELS, 2, model_callback)
        idx = MODELS.index(USERS[camname].target_style)
        url = MANIFEST[idx]['url_gltf']
        USERS[camname].clipboard = arblib.set_clipboard(
            camname, callback=clipboard_callback, obj_type=arena.Shape.gltf_model,
            scale=arblib.SCL_GLTF, url=url)
    elif mode == Mode.COLOR:
        update_dropdown(camname, objid, mode,
                        arblib.COLORS, -2, color_callback)
    elif mode == Mode.OCCLUDE:
        update_dropdown(camname, objid, mode, arblib.BOOLS, -2, gen_callback)
    elif mode == Mode.RENAME:
        USERS[camname].typetext = ""
        update_dropdown(camname, objid, mode, arblib.KEYS, -2, rename_callback)
        USERS[camname].set_textright(USERS[camname].typetext)
    elif mode == Mode.WALL:
        USERS[camname].clipboard = arblib.set_clipboard(  # brick
            camname, obj_type=arena.Shape.cube, callback=wall_callback,
            color=(203, 65, 84), scale=(0.1, 0.05, 0.05))
        USERS[camname].set_textright("Start: tap flush corner.")
    elif mode == Mode.NUDGE:
        update_dropdown(camname, objid, mode, arblib.METERS, 2, gen_callback)
    elif mode == Mode.SCALE:
        update_dropdown(camname, objid, mode, arblib.METERS, 2, gen_callback)
    elif mode == Mode.ROTATE:
        update_dropdown(camname, objid, mode, arblib.DEGREES, 2, gen_callback)


def update_dropdown(camname, objid, mode, options, row, callback):
    # show new dropdown
    if USERS[camname].panel[objid].active:
        followname = USERS[camname].follow.objName
        maxwidth = min(len(options), 10)
        drop_button_offset = -math.floor(maxwidth / 2)
        for i, option in enumerate(options):
            if mode is Mode.COLOR:
                bcolor = tuple(int(option[c:c + 2], 16) for c in (0, 2, 4))
            else:
                bcolor = arblib.CLR_SELECT
            dbutton = arblib.Button(
                camname, mode, (i % maxwidth) + drop_button_offset, row,
                label=option, parent=followname, color=bcolor, drop=option, callback=callback)
            USERS[camname].dbuttons.append(dbutton)
            if (i + 1) % maxwidth == 0:  # next row
                if row < 0:
                    row -= 1
                else:
                    row += 1
        # make default selection
        if mode is Mode.COLOR:
            rcolor = tuple(int(options[0][c:c + 2], 16) for c in (0, 2, 4))
        else:
            rcolor = arblib.CLR_HUDTEXT
        USERS[camname].set_textright(options[0], color=rcolor)
        USERS[camname].target_style = options[0]


def model_callback(event=None):
    if event.event_type != arena.EventType.mousedown:
        return
    obj = event.object_id.split("_")
    camname = event.source
    owner = obj[3] + "_" + obj[4] + "_" + obj[5]  # callback owner in object_id
    if owner != camname:
        return  # only owner may activate
    model = obj[2]
    idx = MODELS.index(model)
    url = MANIFEST[idx]['url_gltf']
    USERS[camname].clipboard = arblib.set_clipboard(
        camname, callback=clipboard_callback, obj_type=arena.Shape.gltf_model,
        scale=arblib.SCL_GLTF, url=url)
    USERS[camname].set_textright(model)
    USERS[camname].target_style = model


def shape_callback(event=None):
    if event.event_type != arena.EventType.mousedown:
        return
    obj = event.object_id.split("_")
    camname = event.source
    owner = obj[3] + "_" + obj[4] + "_" + obj[5]  # callback owner in object_id
    if owner != camname:
        return  # only owner may activate
    shape = obj[2]
    USERS[camname].clipboard = arblib.set_clipboard(
        camname, callback=clipboard_callback, obj_type=arena.Shape(shape))
    USERS[camname].set_textright(shape)
    USERS[camname].target_style = shape


def color_callback(event=None):
    if event.event_type != arena.EventType.mousedown:
        return
    obj = event.object_id.split("_")
    camname = event.source
    owner = obj[3] + "_" + obj[4] + "_" + obj[5]  # callback owner in object_id
    if owner != camname:
        return  # only owner may activate
    hcolor = obj[2]
    color = tuple(int(hcolor[c:c + 2], 16) for c in (0, 2, 4))
    USERS[camname].set_textright(hcolor, color=color)
    USERS[camname].target_style = hcolor


def gen_callback(event=None):
    if event.event_type != arena.EventType.mousedown:
        return
    obj = event.object_id.split("_")
    camname = event.source
    owner = obj[3] + "_" + obj[4] + "_" + obj[5]  # callback owner in object_id
    if owner != camname:
        return  # only owner may activate
    style = obj[2]
    USERS[camname].set_textright(style)
    USERS[camname].target_style = style


def rename_callback(event=None):
    if event.event_type != arena.EventType.mousedown:
        return
    obj = event.object_id.split("_")
    camname = event.source
    owner = obj[3] + "_" + obj[4] + "_" + obj[5]  # callback owner in object_id
    if owner != camname:
        return  # only owner may activate
    key = obj[2]
    USERS[camname].set_textright(key)
    USERS[camname].target_style = key
    if key == 'back':
        if USERS[camname].typetext:
            USERS[camname].typetext = USERS[camname].typetext[:-1]
    else:
        USERS[camname].typetext = USERS[camname].typetext + key
    USERS[camname].set_textright(USERS[camname].typetext)


def show_redpill_scene(enabled):
    # any scene changes must not persist
    # show gridlines
    glen = arblib.GRIDLEN
    y = arblib.FLOOR_Y
    hcolor = arblib.rgb2hex(arblib.CLR_GRID)
    # TODO make thickline?
    for z in range(-glen, glen + 1):
        name = "grid_z" + str(z)
        if enabled:
            arena.Object(objName=name, objType=arena.Shape.line,
                         line=arena.Line((-glen, y, z), (glen, y, z), 1, hcolor))
        else:
            arblib.delete_obj(REALM, SCENE, name)
    for x in range(-glen, glen + 1):
        name = "grid_x" + str(x)
        if enabled:
            arena.Object(objName=name, objType=arena.Shape.line,
                         line=arena.Line((x, y, -glen), (x, y, glen), 1, hcolor))
        else:
            arblib.delete_obj(REALM, SCENE, name)
    pobjs = arblib.get_network_persisted_scene(BROKER, SCENE)
    for pobj in pobjs:
        obj = arblib.ObjectPersistence(pobj)
        # show occulded objects
        if obj.transparent_occlude:
            name = "redpill_" + obj.object_id
            if enabled:
                arena.Object(
                    objName=name,
                    objType=obj.object_type,
                    location=obj.position,
                    rotation=obj.rotation,
                    scale=obj.scale,
                    color=obj.color,  # TODO: needs to use color_material
                    clickable=True,
                    url=obj.url,
                    data=('{"material":{"transparent":true,"opacity":0.5}}'),
                )
                print("Wrapping occlusion " + name)
            else:
                arblib.delete_obj(REALM, SCENE, name)


def do_rename(old_id, new_id):
    pobjs = arblib.get_network_persisted_obj(old_id, BROKER, SCENE)
    if not pobjs:
        return
    data = json.dumps(pobjs[0]["attributes"])
    arena.Object(objName=new_id, data=data)
    print("Duplicating " + old_id + " to " + new_id)
    arblib.delete_obj(REALM, SCENE, old_id)


def show_redpill_obj(camname, object_id):
    # any scene changes must not persist
    pobjs = arblib.get_network_persisted_obj(object_id, BROKER, SCENE)
    if not pobjs:
        return
    obj = arblib.ObjectPersistence(pobjs[0])
    # enable mouse enter/leave pos/rot/scale
    USERS[camname].set_textstatus(object_id + ' p' + str(obj.position) +
                                  ' r' + str(obj.rotation) + ' s' + str(obj.scale))


def do_move_select(camname, object_id):
    pobjs = arblib.get_network_persisted_obj(object_id, BROKER, SCENE)
    if not pobjs:
        return
    obj = arblib.ObjectPersistence(pobjs[0])
    USERS[camname].target_id = object_id
    USERS[camname].clipboard = arblib.set_clipboard(
        camname,
        callback=clipboard_callback,
        obj_type=obj.object_type,
        scale=obj.scale,
        color=obj.color,  # TODO: needs to use color_material
        url=obj.url,
    )


def do_nudge_select(camname, object_id):
    pobjs = arblib.get_network_persisted_obj(object_id, BROKER, SCENE)
    if not pobjs:
        return
    obj = arblib.ObjectPersistence(pobjs[0])
    color = arblib.CLR_NUDGE
    delim = "_click_"
    callback = nudgeline_callback
    # generate child 6dof non-persist, clickable lines
    make_clickline("x", 1, obj, delim, color, callback)
    make_clickline("x", -1, obj, delim, color, callback)
    make_clickline("y", 1, obj, delim, color, callback)
    make_clickline("y", -1, obj, delim, color, callback)
    make_clickline("z", 1, obj, delim, color, callback)
    make_clickline("z", -1, obj, delim, color, callback)
    make_followspot(obj, delim, color)
    pos = obj.position
    position = (round(pos[0], 3), round(pos[1], 3), round(pos[2], 3))
    USERS[camname].set_textright(
        USERS[camname].target_style+" p"+str(position))


def do_scale_select(camname, object_id):
    pobjs = arblib.get_network_persisted_obj(object_id, BROKER, SCENE)
    if not pobjs:
        return
    obj = arblib.ObjectPersistence(pobjs[0])
    color = arblib.CLR_SCALE
    delim = "_click_"
    callback = scaleline_callback
    # generate 2 child non-persist, clickable lines
    make_clickline("x", 1, obj, delim, color, callback)
    make_clickline("x", -1, obj, delim, color, callback)
    make_followspot(obj, delim, color)
    sca = obj.scale
    scale = (round(sca[0], 3), round(sca[1], 3), round(sca[2], 3))
    USERS[camname].set_textright(USERS[camname].target_style+" s"+str(scale))


def do_rotate_select(camname, object_id):
    pobjs = arblib.get_network_persisted_obj(object_id, BROKER, SCENE)
    if not pobjs:
        return
    obj = arblib.ObjectPersistence(pobjs[0])
    color = arblib.CLR_ROTATE
    delim = "_click_"
    callback = rotateline_callback
    # generate child 6dof non-persist, clickable lines
    make_clickline("x", 1, obj, delim, color, callback, True)
    make_clickline("x", -1, obj, delim, color, callback, True)
    make_clickline("y", 1, obj, delim, color, callback, True)
    make_clickline("y", -1, obj, delim, color, callback, True)
    make_clickline("z", 1, obj, delim, color, callback, True)
    make_clickline("z", -1, obj, delim, color, callback, True)
    make_followspot(obj, delim, color)
    rote = arblib.rotation_quat2euler(obj.rotation)
    euler = (round(rote[0], 1), round(rote[1], 1), round(rote[2], 1))
    USERS[camname].set_textright(USERS[camname].target_style+"d r"+str(euler))


def make_followspot(obj, delimiter, color):
    arena.Object(  # follow spot on ground
        objType=arena.Shape.circle,
        objName=(obj.object_id + delimiter + "_spot"),
        scale=obj.scale,
        color=color,
        location=(obj.position[0], arblib.FLOOR_Y, obj.position[2]),
        rotation=(-0.7, 0, 0, 0.7),
        ttl=arblib.TTL_TEMP,
        data=('{"material":{"transparent":true,"opacity":0.5}}'),
    )


def make_clickline(deg, linelen, obj, delimiter, color, callback, ghost=False):
    endx = endy = endz = 0
    object_id = obj.object_id
    start = obj.position
    direction = "p"
    color_control = (255, 0, 0)  # red increase
    if linelen < 0:
        direction = "n"
        color_control = (0, 0, 255)  # blue increase
    if deg == "x":
        endx = linelen * arblib.CLICKLINE_LEN
    elif deg == "y":
        endy = linelen * arblib.CLICKLINE_LEN
    elif deg == "z":
        endz = linelen * arblib.CLICKLINE_LEN
    arena.Object(  # reference line
        # objType=arena.Shape.line,
        objType=arena.Shape.thickline,
        objName=(object_id + delimiter + deg + direction+"_line"),
        # color=color,
        ttl=arblib.TTL_TEMP,
        # data=('{"start": {"x":' + str(start[0]) +
        #      ',"y":' + str(start[1]) +
        #      ',"z":' + str(start[2]) + '}, ' +
        #      '"end": {"x":' + str(start[0]+endx) +
        #      ',"y":' + str(start[1]+endy) +
        #      ',"z":' + str(start[2]+endz) + '}}'),
        thickline=arena.Thickline({
            start, (start[0]+endx, start[1]+endy, start[2]+endz)}, 1, arblib.rgb2hex(color)),
    )
    if ghost:
        arena.Object(  # ghostline aligns to parent rotation
            # objType=arena.Shape.line,
            objType=arena.Shape.thickline,
            objName=(object_id + delimiter + deg + direction+"_ghost"),
            # color=color,
            ttl=arblib.TTL_TEMP,
            parent=object_id,
            # data=('{"start": {"x":0,"y":0,"z":0}, ' +
            #      '"end": {"x":' + str(endx * 10) +
            #      ',"y":' + str(endy * 10) +
            #      ',"z":' + str(endz * 10) + '}}'),
            thickline=arena.Thickline({
                (0, 0, 0), (endx*10, endy*10, endz*10)}, 1, arblib.rgb2hex(color)),
        )
    arena.Object(  # click object
        objType=arena.Shape.sphere,
        objName=(object_id + delimiter + deg + direction),
        color=color_control,
        clickable=True,
        ttl=arblib.TTL_TEMP,
        callback=callback,
        location=(start[0]+endx, start[1]+endy, start[2]+endz),
        scale=(0.05, 0.05, 0.05),
    )


def do_move_relocate(camname, newlocation):
    arblib.move_obj(REALM, SCENE, USERS[camname].target_id, newlocation)
    USERS[camname].clipboard.delete()
    USERS[camname].target_id = None


def incr_pos(coord, incr):
    div = round(coord / incr)
    res = (math.ceil(div) * incr) + incr
    return float('{0:g}'.format(res))


def incr_neg(coord, incr):
    div = round(coord / incr)
    res = (math.floor(div) * incr)-incr
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


def nudgeline_callback(event=None):
    if event.event_type == arena.EventType.mouseenter:
        USERS[event.source].set_textstatus(event.object_id)
    elif event.event_type == arena.EventType.mouseleave:
        USERS[event.source].set_textstatus("")
    # allow any user to nudge an object
    if event.event_type != arena.EventType.mousedown:
        return
    if USERS[event.source].mode != Mode.NUDGE:
        return
    nudge_id = event.object_id.split("_click_")
    object_id = nudge_id[0]
    direction = (nudge_id[1])[:2]
    pobjs = arblib.get_network_persisted_obj(object_id, BROKER, SCENE)
    if not pobjs:
        return
    obj = arblib.ObjectPersistence(pobjs[0])
    nudged = loc = obj.position
    inc = meters_increment(USERS[event.source].target_style)
    if direction == "xp":
        nudged = (incr_pos(loc[0], inc), loc[1], loc[2])
    elif direction == "xn":
        nudged = (incr_neg(loc[0], inc), loc[1], loc[2])
    elif direction == "yp":
        nudged = (loc[0], incr_pos(loc[1], inc), loc[2])
    elif direction == "yn":
        nudged = (loc[0], incr_neg(loc[1], inc), loc[2])
    elif direction == "zp":
        nudged = (loc[0], loc[1], incr_pos(loc[2], inc))
    elif direction == "zn":
        nudged = (loc[0], loc[1], incr_neg(loc[2], inc))
    arblib.move_obj(REALM, SCENE, object_id, nudged)
    print(str(obj.position) + " to " + str(nudged))
    do_nudge_select(event.source, object_id)  # update nudgelines


def scaleline_callback(event=None):
    if event.event_type == arena.EventType.mouseenter:
        USERS[event.source].set_textstatus(event.object_id)
    elif event.event_type == arena.EventType.mouseleave:
        USERS[event.source].set_textstatus("")
    # allow any user to scale an object
    if event.event_type != arena.EventType.mousedown:
        return
    if USERS[event.source].mode != Mode.SCALE:
        return
    scale_id = event.object_id.split("_click_")
    object_id = scale_id[0]
    direction = (scale_id[1])[:2]
    pobjs = arblib.get_network_persisted_obj(object_id, BROKER, SCENE)
    if not pobjs:
        return
    obj = arblib.ObjectPersistence(pobjs[0])
    scaled = sca = obj.scale
    inc = meters_increment(USERS[event.source].target_style)
    if direction == "xp":
        scaled = (incr_pos(sca[0], inc), incr_pos(
            sca[1], inc), incr_pos(sca[2], inc))
    elif direction == "xn":
        scaled = (incr_neg(sca[0], inc), incr_neg(
            sca[1], inc), incr_neg(sca[2], inc))
    if scaled[0] <= 0 or scaled[1] <= 0 or scaled[2] <= 0:
        return
    arblib.scale_obj(REALM, SCENE, object_id, scaled)
    print(str(obj.scale) + " to " + str(scaled))
    do_scale_select(event.source, object_id)  # update scalelines


def rotateline_callback(event=None):
    if event.event_type == arena.EventType.mouseenter:
        USERS[event.source].set_textstatus(event.object_id)
    elif event.event_type == arena.EventType.mouseleave:
        USERS[event.source].set_textstatus("")
    # allow any user to rotate an object
    if event.event_type != arena.EventType.mousedown:
        return
    if USERS[event.source].mode != Mode.ROTATE:
        return
    rotate_id = event.object_id.split("_click_")
    object_id = rotate_id[0]
    direction = (rotate_id[1])[:2]
    pobjs = arblib.get_network_persisted_obj(object_id, BROKER, SCENE)
    if not pobjs:
        return
    obj = arblib.ObjectPersistence(pobjs[0])
    rotated = rot = obj.rotation
    inc = float(USERS[event.source].target_style)
    rot = arblib.rotation_quat2euler(rot)
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
    rotated = arblib.rotation_euler2quat(rotated)
    arblib.rotate_obj(REALM, SCENE, object_id, rotated)
    print(str(obj.rotation) + " to " + str(rotated))
    do_rotate_select(event.source, object_id)  # update rotatelines


def create_obj(clipboard, location):
    randstr = str(random.randrange(0, 1000000))
    # make a copy of static object in place
    new_obj = arena.Object(
        persist=True,
        objName=clipboard.objType.name + "_" + randstr,
        objType=clipboard.objType,
        location=location,
        rotation=(0, 0, 0, 1),  # undo clipboard rotation for visibility
        scale=clipboard.scale,
        color=clipboard.color,
        data='{"material":{"transparent": false}}',
        url=clipboard.url,
        clickable=True)
    print("Created " + new_obj.objName)


def clipboard_callback(event=None):
    if event.event_type != arena.EventType.mousedown:
        return
    obj = event.object_id.split("_")
    camname = event.source
    owner = obj[1] + "_" + obj[2] + "_" + obj[3]  # callback owner in object_id
    if owner != camname:
        return  # only owner may activate
    location = event.position
    # clicked self HUD clipboard
    if USERS[camname].mode == Mode.CREATE or USERS[camname].mode == Mode.MODEL:
        create_obj(USERS[camname].clipboard, location)
    elif USERS[camname].mode == Mode.MOVE:
        do_move_relocate(camname, location)


def wall_callback(event=None):
    if event.event_type != arena.EventType.mousedown:
        return
    obj = event.object_id.split("_")
    camname = event.source
    owner = obj[1] + "_" + obj[2] + "_" + obj[3]  # callback owner in object_id
    if owner != camname:
        return  # only owner may activate
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
    USERS[camname].wloc_start = USERS[camname].location
    USERS[camname].wrot_start = USERS[camname].rotation
    arblib.temp_loc_marker(USERS[camname].wloc_start, (255, 0, 0))
    arblib.temp_rot_marker(USERS[camname].wloc_start,
                           USERS[camname].wrot_start)


def do_wall_end(camname):
    # end (green)
    USERS[camname].wloc_end = USERS[camname].location
    USERS[camname].wrot_end = USERS[camname].rotation
    arblib.temp_loc_marker(USERS[camname].wloc_end, (0, 255, 0))
    arblib.temp_rot_marker(USERS[camname].wloc_end, USERS[camname].wrot_end)


def make_wall(camname):
    # Wall theory: capture two poses and use them to place a wall object.
    # Also assumes first corner easier to capture accurate rotation than last.
    # Click 1: Capture the position and rotation.
    # Click 2: Capture the position only.
    sloc = USERS[camname].wloc_start
    eloc = USERS[camname].wloc_end
    srot = USERS[camname].wrot_start
    erot = USERS[camname].wrot_end
    print("S POS " + str((sloc[0], sloc[1], sloc[2])))
    print("E POS " + str((eloc[0], eloc[1], eloc[2])))
    # center point (blue)
    locx = arena.agran(statistics.median([sloc[0], eloc[0]]))
    locy = arena.agran(statistics.median([sloc[1], eloc[1]]))
    locz = arena.agran(statistics.median([sloc[2], eloc[2]]))
    arblib.temp_loc_marker((locx, locy, locz), (0, 0, 255))
    print("wall position " + str((locx, locy, locz)))
    # rotation
    print("S ROT " + str((srot[0], srot[1], srot[2], srot[3])))
    print("E ROT " + str((erot[0], erot[1], erot[2], erot[3])))
    rotx = arblib.probable_quat(srot[0])
    roty = arblib.probable_quat(srot[1])
    rotz = arblib.probable_quat(srot[2])
    rotw = arblib.probable_quat(srot[3])
    rot = (rotx, roty, rotz, rotw)
    arblib.temp_rot_marker((locx, locy, locz), rot)
    print("wall rotation " + str(rot))
    # which axis to use for wall? use camera gaze
    # TODO: rotation still off
    if (rot in arblib.GAZES[0]):
        height = abs(sloc[1] - eloc[1])
        width = abs(sloc[0] - eloc[0])
    elif (rot in arblib.GAZES[1]):
        height = abs(sloc[1] - eloc[1])
        width = abs(sloc[2] - eloc[2])
    elif (rot in arblib.GAZES[2]):
        height = abs(sloc[2] - eloc[2])
        width = abs(sloc[0] - eloc[0])
    else:
        # TODO: (placeholder) add direction and hypotenuse
        height = abs(sloc[1] - eloc[1])
        width = abs(sloc[0] - eloc[0])
        print("Non-axis parallel rotation: " + str(rot))
    # scale
    scax = width
    scay = height
    scaz = arblib.WALL_WIDTH
    print("wall scale " + str((scax, scay, scaz)))
    # make wall
    randstr = str(random.randrange(0, 1000000))
    new_wall = arena.Object(
        persist=True,
        clickable=True,
        objName="wall_" + randstr,
        objType=arena.Shape.cube,
        location=(locx, locy, locz),
        rotation=(rotx, roty, rotz, rotw),
        scale=(scax, scay, scaz),
        color=(200, 200, 200),
        data=('{"material":{"transparent":true,"opacity":0.5}}'),
    )
    print("Created " + new_wall.objName +
          " r" + str((rotx, roty, rotz, rotw)) +
          " s" + str((scax, scay, scaz)))
    # TODO: remove wall opacity in final wall feature
    # TODO: push wall front side flush with markers (location-(wall/2))


def scene_callback(msg):
    # This is the MQTT message callback function for the scene
    json_msg = json.loads(msg)
    if json_msg["action"] == "create" and json_msg["data"]["object_type"] == "camera":
        # camera updates define users present
        camname = json_msg["object_id"]
        if camname not in USERS:
            USERS[camname] = arblib.User(camname, panel_callback)

        # save camera's attitude in the world
        USERS[camname].location = (json_msg["data"]["position"]["x"],
                                   json_msg["data"]["position"]["y"],
                                   json_msg["data"]["position"]["z"])
        USERS[camname].rotation = (json_msg["data"]["rotation"]["x"],
                                   json_msg["data"]["rotation"]["y"],
                                   json_msg["data"]["rotation"]["z"],
                                   json_msg["data"]["rotation"]["w"])

        rx = json_msg["data"]["rotation"]["x"]
        ry = json_msg["data"]["rotation"]["y"]

        # floating controller
        if not USERS[camname].follow_lock:
            ty = -(ry + USERS[camname].locky) / 0.7 * math.pi / 2
            tx = -(rx + USERS[camname].lockx) / 0.7 * math.pi / 2
            px = arblib.PANEL_RADIUS * -math.cos(ty)
            py = arblib.PANEL_RADIUS * math.sin(tx)
            pz = arblib.PANEL_RADIUS * math.sin(ty)
            USERS[camname].follow.position(location=(px, py, pz))
        # else: # TODO: panel lock location drop is inaccurate
            # users[camname].lockx = rx + arblib.LOCK_XOFF
            # users[camname].locky = -(ry * math.pi) - arblib.LOCK_YOFF

    # mouse event
    elif json_msg["action"] == "clientEvent":
        # print(json_msg["object_id"] + "  " +
        #      json_msg["action"] + "  " + json_msg["type"])
        objid = json_msg["object_id"]
        # camera updates define users present
        camname = json_msg["data"]["source"]
        if camname not in USERS:
            USERS[camname] = arblib.User(camname, panel_callback)

        # show objects with events
        if json_msg["type"] == "mouseenter":
            if USERS[camname].redpill:
                show_redpill_obj(camname, objid)
            else:
                USERS[camname].set_textstatus(objid)
        elif json_msg["type"] == "mouseleave":
            USERS[camname].set_textstatus("")

        # handle click
        elif json_msg["type"] == "mousedown":
            # clicked on persisted object to modify
            if USERS[camname].mode == Mode.DELETE:
                arblib.delete_obj(REALM, SCENE, objid)
            elif USERS[camname].mode == Mode.MOVE:
                do_move_select(camname, objid)
            elif USERS[camname].mode == Mode.NUDGE:
                do_nudge_select(camname, objid)
            elif USERS[camname].mode == Mode.SCALE:
                do_scale_select(camname, objid)
            elif USERS[camname].mode == Mode.ROTATE:
                do_rotate_select(camname, objid)
            elif USERS[camname].mode == Mode.COLOR:
                arblib.color_obj(REALM, SCENE, objid,
                                 USERS[camname].target_style)
            elif USERS[camname].mode == Mode.OCCLUDE:
                arblib.occlude_obj(REALM, SCENE, objid,
                                   USERS[camname].target_style)
            elif USERS[camname].mode == Mode.RENAME:
                new_id = USERS[camname].typetext
                USERS[camname].typetext = ""
                do_rename(objid, new_id)


# parse args and wait for events
init_args()
random.seed()
arena.init(BROKER, REALM, SCENE, scene_callback)
arena.handle_events()
