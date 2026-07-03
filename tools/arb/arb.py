# arb.py
#
# AR Builder
# Pass in args for scene name and/or broker and realm.

import json
import math
import random
import statistics

import arblib
from arblib import (
    EVT_MOUSEDOWN, EVT_MOUSEENTER, EVT_MOUSELEAVE,
    ButtonType, Mode,
)

from arena import (
    Box, Circle, Color, Cone, Event, GLTF, GltfModel, Light, Line, Material,
    Object, Position, Rotation, Scale, Scene, Text, ThickLine,
)


def get_data_attr(obj, attr, default=None):
    """Safely extract a data attribute from an ARENA object, with a fallback default."""
    if default is None:
        defaults = {
            "position": Position(),
            "rotation": Rotation(),
            "scale": Scale(),
        }
        default = defaults.get(attr)
    return getattr(obj.data, attr) if attr in obj.data else default


class ArbApp:
    """AR Builder application. Encapsulates all state and callbacks."""

    def __init__(self):
        random.seed()
        self.manifest = arblib.DEF_MANIFEST
        self.models = [m['name'] for m in self.manifest]
        self.users = {}   # dictionary of user instances
        self.controls = {}  # dictionary of active controls

        self.scene = Scene(
            cli_args={"manifest": "JSON file path of optional GLTF models to import and place at will."},
            on_msg_callback=self.scene_callback,
            user_join_callback=self.user_join_callback,
            user_left_callback=self.user_left_callback,
            end_program_callback=self.end_program_callback,
        )
        self._init_args()

    def _init_args(self):
        manifest_path = self.scene.args.get("manifest")
        if manifest_path:
            with open(manifest_path) as mfile:
                data = json.load(mfile)
            self.manifest = data['models']
        self.models = [m['name'] for m in self.manifest]
        print(f"ARB Model Manifest: {self.manifest}")

    def run(self):
        self.scene.run_tasks()

    # ------------------------------------------------------------------ #
    #  User lifecycle                                                      #
    # ------------------------------------------------------------------ #

    def user_join_callback(self, _scene, cam, msg):
        """Called when a user joins the scene. Creates the per-user ARB panel."""
        camname = cam.object_id
        print(f"ARB user joined: {camname}")
        self.users[camname] = arblib.User(
            self.scene, camname, self.panel_callback, userid=camname)

    def user_left_callback(self, _scene, cam, msg):
        """Called when a user leaves. Cleans up all per-user objects."""
        camname = cam.object_id
        if camname not in self.users:
            return
        print(f"ARB user left: {camname}")
        # clean up per-user redpill objects
        for obj_id in self.users[camname].redpill_objects:
            arblib.delete_obj(self.scene, obj_id)
        # clean up per-user controls
        for objid in list(self.controls.keys()):
            for ctrl_name in list(self.controls[objid].keys()):
                if camname in ctrl_name:
                    self.scene.delete_object(self.controls[objid][ctrl_name])
                    del self.controls[objid][ctrl_name]
        # clean up user HUD, panel, clipboard, lamp
        self.users[camname].delete()
        del self.users[camname]

    # ------------------------------------------------------------------ #
    #  Event handling helpers                                              #
    # ------------------------------------------------------------------ #

    def handle_panel_event(self, evt, dropdown=False):
        # Private channels ensure only the owner receives events for their buttons
        drop = None
        camname = evt.object_id
        objid = evt.data.target
        if camname not in self.users:
            return None, None, None
        if evt.type == EVT_MOUSEENTER or evt.type == EVT_MOUSELEAVE:
            if evt.type == EVT_MOUSEENTER:
                hover = True
            elif evt.type == EVT_MOUSELEAVE:
                hover = False
            if dropdown:
                if objid in self.users[camname].dbuttons:
                    self.users[camname].dbuttons[objid].set_hover(hover)
            else:
                if objid in self.users[camname].panel:
                    self.users[camname].panel[objid].set_hover(hover)

        if evt.type != EVT_MOUSEDOWN:
            return None, None, None
        if dropdown and objid in self.users[camname].dbuttons:
            drop = self.users[camname].dbuttons[objid].dropdown
        return (camname, objid, drop)

    def handle_clip_event(self, evt):
        # Private channels ensure only the owner receives events for their clipboard
        camname = evt.object_id
        if camname not in self.users:
            return None
        if evt.type != EVT_MOUSEDOWN:
            return None
        return camname

    def handle_clickline_event(self, evt, mode):
        camname = evt.object_id
        val = 0
        # naming order: object-name_mode_axis-move_direction
        if self.users[camname].target_control_id and (evt.type.startswith("twofinger") or self.users[camname].gesturing):
            ctrl_object_id = self.users[camname].target_control_id
        else:
            ctrl_object_id = evt.data.target  # v2: target is the clicked object
        click_id = ctrl_object_id.split(f"_{mode.value}_")
        object_id = click_id[0]
        if not self.users[camname].target_control_id and not self.users[camname].gesturing and evt.data.target == camname:
            return None, None, None, val
        direction = (click_id[1])[0:2]
        move = (click_id[1])[1:4]
        if evt.type == EVT_MOUSEENTER:
            if not self.users[camname].gesturing:
                self.scene.update_object(
                    self.controls[object_id][ctrl_object_id],
                    material=Material(transparent=True, opacity=arblib.OPC_CLINE_HOVER))
                # set controller target
                self.users[camname].target_control_id = ctrl_object_id
        elif evt.type == EVT_MOUSELEAVE:
            if not self.users[camname].gesturing:
                self.scene.update_object(
                    self.controls[object_id][ctrl_object_id],
                    material=Material(transparent=True, opacity=arblib.OPC_CLINE))
                # release controller target
                self.users[camname].target_control_id = None

        # handle gestures
        elif evt.type == "twofingerstart":
            # start hold down event for both clickers
            self.users[camname].gesturing = True
            self.scene.update_object(
                self.controls[object_id][f"{object_id}_{mode.value}_{(click_id[1])[0:1]}p{(click_id[1])[2:4]}"],
                material=Material(transparent=True, opacity=arblib.OPC_CLINE_HOVER))
            self.scene.update_object(
                self.controls[object_id][f"{object_id}_{mode.value}_{(click_id[1])[0:1]}n{(click_id[1])[2:4]}"],
                material=Material(transparent=True, opacity=arblib.OPC_CLINE_HOVER))
        elif evt.type == "twofingerend":
            # release hold down event for both clickers
            if self.users[camname].gesturing:
                self.scene.update_object(
                    self.controls[object_id][f"{object_id}_{mode.value}_{(click_id[1])[0:1]}p{(click_id[1])[2:4]}"],
                    material=Material(transparent=True, opacity=arblib.OPC_CLINE))
                self.scene.update_object(
                    self.controls[object_id][f"{object_id}_{mode.value}_{(click_id[1])[0:1]}n{(click_id[1])[2:4]}"],
                    material=Material(transparent=True, opacity=arblib.OPC_CLINE))
                # release controller target
                self.users[camname].target_control_id = None
                self.users[camname].gesturing = False
        elif evt.type == "twofingermove" and self.users[camname].slider:
            # send slider movement for clickers
            if self.users[camname].gesturing:
                obj = self.scene.get_persisted_obj(object_id)
                # determine direction of 2d gesture in 3d
                if click_id[1][0] == "y":
                    val = evt.data.positionStart.y - evt.data.targetPosition.y
                elif click_id[1][0] == "x":
                    if evt.data.originPosition.z > obj.data.position.z:
                        val = evt.data.positionStart.x - evt.data.targetPosition.x
                    else:
                        val = evt.data.positionStart.x + evt.data.targetPosition.x
                else:  # click_id[1][0] == "z":
                    if evt.data.originPosition.x < obj.data.position.x:
                        val = evt.data.positionStart.x - evt.data.targetPosition.x
                    else:
                        val = evt.data.positionStart.x + evt.data.targetPosition.x
                if val >= 0:
                    direction = f"{(click_id[1])[0:1]}p"
                    move = f"p{(click_id[1])[2:4]}"
                else:
                    direction = f"{(click_id[1])[0:1]}n"
                    move = f"n{(click_id[1])[2:4]}"
                return (obj, direction, move, abs(val))
        else:
            # send camera movement for clickers
            if self.users[camname].gesturing:
                obj = self.scene.get_persisted_obj(object_id)
                # determine direction of 2d gesture in 3d
                if mode == Mode.ROTATE:  # rotation based: rotate
                    try:
                        rot_last = arblib.rotation_quat2euler(
                            (self.users[camname].rotation_last.x, self.users[camname].rotation_last.y, self.users[camname].rotation_last.z, self.users[camname].rotation_last.w))
                        rot = arblib.rotation_quat2euler(
                            (self.users[camname].rotation.x, self.users[camname].rotation.y, self.users[camname].rotation.z, self.users[camname].rotation.w))
                        if click_id[1][0] == "y":
                            val = -(rot_last[1] - rot[1])
                        elif click_id[1][0] == "x":
                            val = -(rot_last[0] - rot[0])
                        else:  # click_id[1][0] == "z":
                            val = -(rot_last[2] - rot[2])
                    except ValueError as error:
                        print(f"Rotation error: {error}")
                        return None, None, None, val
                else:  # position based: nudge, scale, stretch
                    if click_id[1][0] == "y":
                        val = -(self.users[camname].position_last.y -
                                self.users[camname].position.y)
                    elif click_id[1][0] == "x":
                        val = -(self.users[camname].position_last.x -
                                self.users[camname].position.x)
                    else:  # click_id[1][0] == "z":
                        val = -(self.users[camname].position_last.z -
                                self.users[camname].position.z)
                if val >= 0:
                    direction = f"{(click_id[1])[0:1]}p"
                    move = f"p{(click_id[1])[2:4]}"
                else:
                    direction = f"{(click_id[1])[0:1]}n"
                    move = f"n{(click_id[1])[2:4]}"
                return (obj, direction, move, abs(val))

        # allow any user to change an object
        if evt.type != EVT_MOUSEDOWN:
            return None, None, None, val
        if self.users[camname].mode != mode:
            return None, None, None, val
        obj = self.scene.get_persisted_obj(object_id)
        return (obj, direction, move, val)

    # ------------------------------------------------------------------ #
    #  Panel callback and dropdown management                              #
    # ------------------------------------------------------------------ #

    def panel_callback(self, _scene, evt, msg):
        camname, objid, drop = self.handle_panel_event(evt)
        if not camname or not objid:
            return
        # ignore disabled
        if not self.users[camname].panel[objid].enabled:
            return

        self.update_controls(self.users[camname].target_id)
        mode = self.users[camname].panel[objid].mode
        btype = self.users[camname].panel[objid].type
        if btype == ButtonType.TOGGLE:
            self.users[camname].panel[objid].set_active(
                not self.users[camname].panel[objid].active)
        else:
            if mode == self.users[camname].mode:  # action cancel
                # button click is same, then goes off and NONE
                self.users[camname].panel[objid].set_active(False)
                self.users[camname].mode = Mode.NONE
                mode = Mode.NONE
            else:
                # if button goes on, last button must go off
                prev_objid = f"{camname}_button_{self.users[camname].mode.value}"
                if prev_objid in self.users[camname].panel:
                    self.users[camname].panel[prev_objid].set_active(False)
                self.users[camname].panel[objid].set_active(True)
                self.users[camname].mode = mode
            self.users[camname].set_textleft(self.users[camname].mode)
            self.users[camname].set_textright("")
            self.users[camname].del_clipboard()
            # clear last dropdown
            for but in self.users[camname].dbuttons:
                self.users[camname].dbuttons[but].delete()
            self.users[camname].dbuttons.clear()

        active = self.users[camname].panel[objid].active
        # toggle buttons
        if mode == Mode.LOCK:
            self.users[camname].follow_lock = active
            # ENHANCEMENT: after lock ensure original ray keeps lock button in reticle
        elif mode == Mode.REDPILL:
            self.users[camname].redpill = active
            self.show_redpill_scene(camname, active)
        elif mode == Mode.LAMP:
            self.users[camname].set_lamp(active)
        elif mode == Mode.SLIDER:
            self.users[camname].slider = active
        elif mode == Mode.EDIT:
            self.users[camname].set_clickableOnlyEvents(active)
            self.users[camname].set_textright("SCENE-OPTIONS changed: RELOAD")
        # active buttons
        if mode == Mode.CREATE:
            self.update_dropdown(camname, objid, mode, arblib.SHAPES, 2, self.shape_callback)
            self.users[camname].set_clipboard(
                callback=self.clipboard_callback,
                object_type=self.users[camname].target_style)
        elif mode == Mode.MODEL:
            self.update_dropdown(camname, objid, mode, self.models, 2, self.model_callback)
            idx = self.models.index(self.users[camname].target_style)
            url = self.manifest[idx]['url_gltf']
            sca = self.manifest[idx]['scale']
            self.users[camname].set_clipboard(
                callback=self.clipboard_callback, object_type=GLTF.object_type,
                scale=Scale(sca, sca, sca), url=url)
        elif mode == Mode.COLOR:
            self.update_dropdown(camname, objid, mode,
                            arblib.COLORS, -2, self.color_callback)
        elif mode == Mode.OCCLUDE:
            self.update_dropdown(camname, objid, mode, arblib.BOOLS, -2, self.gen_callback)
        elif mode == Mode.RENAME:
            self.users[camname].typetext = ""
            self.update_dropdown(camname, objid, mode, arblib.KEYS, -2, self.rename_callback)
            self.users[camname].set_textright(self.users[camname].typetext)
        elif mode == Mode.PARENT:
            self.users[camname].typetext = ""
            self.users[camname].set_textright(self.users[camname].typetext)
        elif mode == Mode.WALL:
            self.users[camname].set_clipboard(callback=self.wall_callback)
            self.users[camname].set_textright("Start: tap flush corner.")
        elif mode == Mode.NUDGE:
            self.update_dropdown(camname, objid, mode, arblib.METERS, 2, self.gen_callback)
            if self.users[camname].target_id:
                self.do_nudge_select(camname, self.users[camname].target_id)
        elif mode == Mode.SCALE:
            self.update_dropdown(camname, objid, mode, arblib.METERS, 2, self.gen_callback)
            if self.users[camname].target_id:
                self.do_scale_select(camname, self.users[camname].target_id)
        elif mode == Mode.STRETCH:
            self.update_dropdown(camname, objid, mode, arblib.METERS, 2, self.gen_callback)
            if self.users[camname].target_id:
                self.do_stretch_select(camname, self.users[camname].target_id)
        elif mode == Mode.ROTATE:
            self.update_dropdown(camname, objid, mode, arblib.DEGREES, 2, self.gen_callback)
            if self.users[camname].target_id:
                self.do_rotate_select(camname, self.users[camname].target_id)

    def update_dropdown(self, camname, objid, mode, options, row, callback):
        # show new dropdown
        if self.users[camname].panel[objid].active:
            followname = self.users[camname].follow.object_id
            maxwidth = min(len(options), 10)
            drop_button_offset = -math.floor(maxwidth / 2)
            for i, option in enumerate(options):
                if mode is Mode.COLOR:
                    bcolor = Color(option)
                else:
                    bcolor = arblib.CLR_SELECT
                dbutton = arblib.Button(
                    self.scene, camname, mode, (i % maxwidth) + drop_button_offset, row,
                    label=option, parent=followname, color=bcolor, drop=option,
                    callback=callback, private_userid=camname)
                self.users[camname].dbuttons[dbutton.button.object_id] = dbutton
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
            self.users[camname].set_textright(options[0], color=rcolor)
            self.users[camname].target_style = options[0]

    # ------------------------------------------------------------------ #
    #  Dropdown item callbacks                                             #
    # ------------------------------------------------------------------ #

    def model_callback(self, _scene, evt, msg):
        camname, objid, drop = self.handle_panel_event(evt, dropdown=True)
        if not camname or not drop:
            return
        model = drop
        idx = self.models.index(model)
        url = self.manifest[idx]['url_gltf']
        sca = self.manifest[idx]['scale']
        self.users[camname].set_clipboard(
            callback=self.clipboard_callback, object_type=GLTF.object_type,
            scale=Scale(sca, sca, sca), url=url)
        self.users[camname].set_textright(model)
        self.users[camname].target_style = model

    def shape_callback(self, _scene, evt, msg):
        camname, objid, drop = self.handle_panel_event(evt, dropdown=True)
        if not camname or not drop:
            return
        shape = drop
        self.users[camname].set_clipboard(
            callback=self.clipboard_callback, object_type=shape)
        self.users[camname].set_textright(shape)
        self.users[camname].target_style = shape

    def color_callback(self, _scene, evt, msg):
        camname, objid, drop = self.handle_panel_event(evt, dropdown=True)
        if not camname or not objid:
            return
        hcolor = drop
        color = Color(hcolor)
        self.users[camname].set_textright(hcolor, color=color)
        self.users[camname].target_style = hcolor

    def gen_callback(self, _scene, evt, msg):
        camname, objid, drop = self.handle_panel_event(evt, dropdown=True)
        if not camname or not drop:
            return
        style = drop
        self.users[camname].set_textright(style)
        self.users[camname].target_style = style

    def rename_callback(self, _scene, evt, msg):
        camname, objid, drop = self.handle_panel_event(evt, dropdown=True)
        if not camname or not drop:
            return
        key = drop
        self.users[camname].set_textright(key)
        self.users[camname].target_style = key
        if key == 'back':
            if len(self.users[camname].typetext) > 0:
                self.users[camname].typetext = self.users[camname].typetext[:-1]
        elif key == 'underline':
            self.users[camname].typetext = f"{self.users[camname].typetext}_"
        elif key == 'apriltag':  # special prefix, replace text with 'apriltag_'
            self.users[camname].typetext = 'apriltag_'
        else:
            self.users[camname].typetext = self.users[camname].typetext + key
        self.users[camname].set_textright(self.users[camname].typetext)

    # ------------------------------------------------------------------ #
    #  Redpill mode                                                        #
    # ------------------------------------------------------------------ #

    def show_redpill_scene(self, camname, enabled):
        # any scene changes must not persist; redpill is per-user (private)
        userid = self.users[camname].userid
        # show gridlines
        name = f"grid_redpill_{camname}"
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
            self.scene.add_object(ThickLine(
                object_id=name,
                path=path,
                color=arblib.CLR_GRID,
                private_userid=userid))
            self.users[camname].redpill_objects.append(name)
        else:
            arblib.delete_obj(self.scene, name)
            if name in self.users[camname].redpill_objects:
                self.users[camname].redpill_objects.remove(name)

        objs = self.scene.get_persisted_objs()
        for object_id in objs:
            obj = objs[object_id]
            # show occluded objects
            if "material-extras" in obj.data and "transparentOccluder" in obj.data["material-extras"]:
                name = f"redpill_{camname}_{obj.object_id}"
                if enabled:
                    object_type = get_data_attr(obj, "object_type", "box")
                    position = get_data_attr(obj, "position")
                    rotation = get_data_attr(obj, "rotation")
                    scale = get_data_attr(obj, "scale")
                    url = get_data_attr(obj, "url", None)
                    color = Color()
                    if "material" in obj.data and "color" in obj.data.material:
                        color = obj.data.material.color
                    self.scene.add_object(Object(
                        object_id=name,
                        object_type=object_type,
                        position=position,
                        rotation=rotation,
                        scale=scale,
                        url=url,
                        material=Material(
                            color=color, transparent=True, opacity=arblib.OPC_TRANSLUCENT),
                        private_userid=userid,
                    ))
                    self.users[camname].redpill_objects.append(name)
                    print("Wrapping occlusion " + name)
                else:
                    arblib.delete_obj(self.scene, name)
                    if name in self.users[camname].redpill_objects:
                        self.users[camname].redpill_objects.remove(name)

    # ------------------------------------------------------------------ #
    #  Object operations                                                   #
    # ------------------------------------------------------------------ #

    def do_rename(self, camname, old_id, new_id):
        if new_id == old_id:
            return
        obj = self.scene.get_persisted_obj(old_id)
        self.scene.add_object(
            Object(object_id=new_id, persist=obj.persist, **obj.data.__dict__))
        if new_id in self.scene.all_objects:
            self.users[camname].target_id = new_id
            print(f"Duplicating {old_id} to {new_id}")
            arblib.delete_obj(self.scene, old_id)

    def show_redpill_obj(self, camname, object_id):
        # any scene changes must not persist
        obj = self.scene.get_persisted_obj(object_id)
        # enable mouse enter/leave pos/rot/scale
        position = get_data_attr(obj, "position")
        rotation = get_data_attr(obj, "rotation")
        scale = get_data_attr(obj, "scale")
        self.users[camname].set_textstatus(
            " ".join([f"{object_id}",
                      f"p({position.x},{position.y},{position.z})",
                      f"r({rotation.x},{rotation.y},{rotation.z},{rotation.w})",
                      f"s({scale.x},{scale.y},{scale.z})"]))

    def do_move_select(self, camname, object_id):
        obj = self.scene.get_persisted_obj(object_id)
        self.users[camname].target_id = object_id
        object_type = get_data_attr(obj, "object_type", "box")
        scale = get_data_attr(obj, "scale")
        color = Color()
        if "material" in obj.data and "color" in obj.data.material:
            color = obj.data.material.color
        url = get_data_attr(obj, "url", None)
        self.users[camname].set_clipboard(
            callback=self.clipboard_callback,
            object_type=object_type,
            scale=scale,
            color=color,
            url=url,
        )

    # ------------------------------------------------------------------ #
    #  Controls (clicklines, clickroots)                                   #
    # ------------------------------------------------------------------ #

    def update_controls(self, objid):
        if objid not in self.controls.keys():
            self.controls[objid] = {}
        for ctrl in self.controls[objid]:
            self.scene.delete_object(self.controls[objid][ctrl])
        self.controls[objid].clear()

    def do_nudge_select(self, camname, objid, position=None):
        color = arblib.CLR_NUDGE
        delim = f"_{Mode.NUDGE.value}_"
        callback = self.nudgeline_callback
        obj = self.scene.get_persisted_obj(objid)
        if not position:
            position = get_data_attr(obj, "position")
        xl, yl, zl = self.get_clicklines_len(obj)
        # nudge object + or - on 3 axis
        root = self.make_clickroot(objid, position, delim, move=True,
                                   private_userid=camname)
        self.make_clickline("x", xl, objid, position, delim, color,
                       callback, move=True, parent=root, private_userid=camname)
        self.make_clickline("y", yl, objid, position, delim, color,
                       callback, move=True, parent=root, private_userid=camname)
        self.make_clickline("z", zl, objid, position, delim, color,
                       callback, move=True, parent=root, private_userid=camname)
        # ENHANCEMENT: restore make_followspot(objid, position, delim, color, move=True)
        pos = Position(round(position.x, 3), round(
            position.y, 3), round(position.z, 3))
        self.users[camname].set_textright(
            f"{self.users[camname].target_style} p({pos.x},{pos.y},{pos.z})")

    def do_scale_select(self, camname, objid, scale=None):
        color = arblib.CLR_SCALE
        delim = f"_{Mode.SCALE.value}_"
        callback = self.scaleline_callback
        obj = self.scene.get_persisted_obj(objid)
        position = get_data_attr(obj, "position")
        if not scale:
            scale = get_data_attr(obj, "scale")
        xl, yl, zl = self.get_clicklines_len(obj)
        # scale entire object + or - on all axis
        root = self.make_clickroot(objid, position, delim, move=True,
                                   private_userid=camname)
        self.make_clickline("x", xl, objid, position, delim, color,
                       callback, move=True, parent=root, private_userid=camname)
        # ENHANCEMENT: restore make_followspot(objid, position, delim, color)
        sca = Scale(round(scale.x, 3), round(scale.y, 3), round(scale.z, 3))
        self.users[camname].set_textright(
            f"{self.users[camname].target_style} s({sca.x},{sca.y},{sca.z})")

    def do_stretch_select(self, camname, objid, scale=None):
        color = arblib.CLR_STRETCH
        delim = f"_{Mode.STRETCH.value}_"
        callback = self.stretchline_callback
        obj = self.scene.get_persisted_obj(objid)
        position = get_data_attr(obj, "position")
        if not scale:
            object_type = get_data_attr(obj, "object_type", "box")
            rotation = get_data_attr(obj, "rotation")
            scale = get_data_attr(obj, "scale")
            # FIXME: GLTF scale too unpredictable to stretch; needs mesh bounding box
            if object_type == GLTF.object_type:
                return
            # FIXME: non-identity rotation makes stretch axis ambiguous
            if rotation.quaternion.__dict__ != Rotation(x=0, y=0, z=0, w=1).quaternion.__dict__:
                return
        xl, yl, zl = self.get_clicklines_len(obj)
        # scale and reposition on one of 6 sides
        root = self.make_clickroot(objid, position, delim, move=True,
                                   private_userid=camname)
        self.make_clickline("x", xl, objid, position, delim, color,
                       callback, move=True, parent=root, private_userid=camname)
        self.make_clickline("x", -xl, objid, position, delim,
                       color, callback, move=True, parent=root, private_userid=camname)
        self.make_clickline("y", yl, objid, position, delim, color,
                       callback, move=True, parent=root, private_userid=camname)
        self.make_clickline("y", -yl, objid, position, delim,
                       color, callback, move=True, parent=root, private_userid=camname)
        self.make_clickline("z", zl, objid, position, delim, color,
                       callback, move=True, parent=root, private_userid=camname)
        self.make_clickline("z", -zl, objid, position, delim,
                       color, callback, move=True, parent=root, private_userid=camname)
        # ENHANCEMENT: restore make_followspot(objid, position, delim, color)
        sca = Scale(round(scale.x, 3), round(scale.y, 3), round(scale.z, 3))
        self.users[camname].set_textright(
            f"{self.users[camname].target_style} s({sca.x},{sca.y},{sca.z})")

    def do_rotate_select(self, camname, objid, rotation=None):
        color = arblib.CLR_ROTATE
        delim = f"_{Mode.ROTATE.value}_"
        callback = self.rotateline_callback
        obj = self.scene.get_persisted_obj(objid)
        position = get_data_attr(obj, "position")
        if not rotation:
            rotation = get_data_attr(obj, "rotation")
        xl, yl, zl = self.get_clicklines_len(obj)
        # rotate object + or - on 3 axis, plus show original axis as after
        # effect
        root = self.make_clickroot(objid, position, delim,
                                   private_userid=camname)
        ghost = self.make_clickroot(objid, position, delim,
                               rotation=rotation, move=True, private_userid=camname)
        self.make_clickline("x", xl, objid, position, delim, color,
                       callback, ghost=ghost, parent=root, private_userid=camname)
        self.make_clickline("y", yl, objid, position, delim, color,
                       callback, ghost=ghost, parent=root, private_userid=camname)
        self.make_clickline("z", zl, objid, position, delim, color,
                       callback, ghost=ghost, parent=root, private_userid=camname)
        # ENHANCEMENT: restore make_followspot(objid, position, delim, color)
        try:
            rote = arblib.rotation_quat2euler(
                (rotation.x, rotation.y, rotation.z, rotation.w))
        except ValueError as error:
            print(f"Rotation error: {error}")
            return
        euler = (round(rote[0], 1), round(rote[1], 1), round(rote[2], 1))
        self.users[camname].set_textright(
            f"{self.users[camname].target_style}d r({euler[0]},{euler[1]},{euler[2]})")

    def get_clicklines_len(self, obj):
        object_type = get_data_attr(obj, "object_type", "box")
        scale = get_data_attr(obj, "scale")
        if object_type == "gltf-model":
            # FIXME: if we can get the GLTF bounding box (not scale), we can make accurate clicklines
            scale = Scale(0.1, 0.1, 0.1)
            line_extension = arblib.CLICKLINE_LEN_MOD
        else:
            line_extension = arblib.CLICKLINE_LEN_OBJ
        xl = scale.x + line_extension
        yl = scale.y + line_extension
        zl = scale.z + line_extension
        return xl, yl, zl

    def make_followspot(self, object_id, position, delim, color, parent,
                        move=False, private_userid=None):
        name = f"{object_id}{delim}spot"
        if name not in self.controls[object_id]:
            self.controls[object_id][name] = Circle(  # follow spot on ground
                object_id=name,
                scale=Scale(0.1, 0.1, 0.1),
                # ENHANCEMENT: restore ttl=arblib.TTL_TEMP,
                position=Position(position.x, arblib.FLOOR_Y, position.z),
                rotation=arblib.ROT_FACE_DOWN,
                parent=parent,
                material=Material(
                    color=color,
                    transparent=True,
                    opacity=arblib.OPC_OVERLAY,
                    shader="flat"),
                private_userid=private_userid,
            )
            self.scene.add_object(self.controls[object_id][name])
        elif move:
            self.scene.update_object(self.controls[object_id][name], position=position)

    def regline(self, object_id, axis, direction, delim, suffix, start,
                end, line_width, move, color, parent, private_userid=None):
        line_width = line_width/arblib.SCL_CLICK
        end = Position(x=(end.x - start.x)/arblib.SCL_CLICK,
                       y=(end.y - start.y)/arblib.SCL_CLICK,
                       z=(end.z - start.z)/arblib.SCL_CLICK)
        name = f"{object_id}{delim}{axis}{direction}_{suffix}"
        if name not in self.controls[object_id]:
            self.controls[object_id][name] = Line(
                object_id=name,
                color=color,
                # ENHANCEMENT: restore ttl=arblib.TTL_TEMP,
                parent=parent,
                start=start,
                end=end,
                private_userid=private_userid)
            self.scene.add_object(self.controls[object_id][name])
        elif move:
            self.scene.update_object(self.controls[object_id][name], start=start, end=end)

    def boxline(self, object_id, axis, direction, delim, suffix, start,
                end, line_width, move, color, parent, private_userid=None):
        line_width = line_width/arblib.SCL_CLICK
        end = Position(x=(end.x - start.x)/arblib.SCL_CLICK,
                       y=(end.y - start.y)/arblib.SCL_CLICK,
                       z=(end.z - start.z)/arblib.SCL_CLICK)
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
        if name not in self.controls[object_id]:
            self.controls[object_id][name] = Box(
                object_id=name,
                # ENHANCEMENT: restore ttl=arblib.TTL_TEMP,
                parent=parent,
                scale=scale,
                position=position,
                material=Material(
                    color=color,
                    transparent=True,
                    opacity=arblib.OPC_OVERLAY,
                    shader="flat"),
                private_userid=private_userid,
            )
            self.scene.add_object(self.controls[object_id][name])
        elif move:
            self.scene.update_object(self.controls[object_id][name],
                                position=position, scale=scale)

    def dir_clickers(self, object_id, axis, direction, delim, position,
                     color, cones, callback, move, parent, private_userid=None):
        position = Position(x=position.x/arblib.SCL_CLICK,
                            y=position.y/arblib.SCL_CLICK,
                            z=position.z/arblib.SCL_CLICK)
        loc = Position(x=position.x/arblib.SCL_CLICK,
                       y=position.y/arblib.SCL_CLICK,
                       z=position.z/arblib.SCL_CLICK)
        npos = arblib.CONE_OFFSET/arblib.SCL_CLICK
        if direction == "p":
            npos = -arblib.CONE_OFFSET/arblib.SCL_CLICK
        if axis == "x":
            loc = Position(x=position.x + npos, y=position.y, z=position.z)
        elif axis == "y":
            loc = Position(x=position.x, y=position.y + npos, z=position.z)
        elif axis == "z":
            loc = Position(x=position.x, y=position.y, z=position.z + npos)
        name_pos = f"{object_id}{delim}{axis}p_{direction}"
        name_neg = f"{object_id}{delim}{axis}n_{direction}"
        if name_pos not in self.controls[object_id]:
            self.controls[object_id][name_pos] = Cone(   # click object positive
                object_id=name_pos,
                clickable=True,
                position=position,
                rotation=cones[axis + direction][0],
                scale=Scale(arblib.SCL_CONE_RADIUS/arblib.SCL_CLICK, arblib.SCL_CONE_HEIGHT/arblib.SCL_CLICK, arblib.SCL_CONE_RADIUS/arblib.SCL_CLICK),
                material=Material(color=color, transparent=True,
                                  opacity=arblib.OPC_CLINE),
                # ENHANCEMENT: restore ttl=arblib.TTL_TEMP,
                parent=parent,
                evt_handler=callback,
                private_userid=private_userid)
            self.scene.add_object(self.controls[object_id][name_pos])
        elif move:
            self.scene.update_object(self.controls[object_id][name_pos], position=position)
        if name_neg not in self.controls[object_id]:
            self.controls[object_id][name_neg] = Cone(  # click object negative
                object_id=name_neg,
                clickable=True,
                position=loc,
                rotation=cones[axis + direction][1],
                scale=Scale(arblib.SCL_CONE_RADIUS/arblib.SCL_CLICK, arblib.SCL_CONE_HEIGHT/arblib.SCL_CLICK, arblib.SCL_CONE_RADIUS/arblib.SCL_CLICK),
                material=Material(color=color, transparent=True,
                                  opacity=arblib.OPC_CLINE),
                # ENHANCEMENT: restore ttl=arblib.TTL_TEMP,
                parent=parent,
                evt_handler=callback,
                private_userid=private_userid)
            self.scene.add_object(self.controls[object_id][name_neg])
        elif move:
            self.scene.update_object(self.controls[object_id][name_neg], position=loc)

    def make_clickline(self, axis, linelen, objid, start, delim,
                       color, callback, ghost=None, parent=None, move=False,
                       private_userid=None):
        if objid not in self.controls.keys():
            self.controls[objid] = {}
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
        self.boxline(  # reference line
            object_id=objid, axis=axis, direction=direction, delim=delim,
            suffix="line", color=color, start=start, end=end, line_width=arblib.CLICKLINE_WIDTH, move=move,
            parent=parent, private_userid=private_userid)
        if ghost:
            self.boxline(  # ghostline aligns to parent rotation
                object_id=objid, axis=axis, direction=direction, delim=delim,
                suffix="ghost", color=(255, 255, 255), start=start, end=end, line_width=arblib.CLICKLINE_WIDTH,
                move=move, parent=ghost, private_userid=private_userid)
        if ghost:
            cones = arblib.ROTATE_CONES
        else:
            cones = arblib.DIRECT_CONES
        self.dir_clickers(  # click objects
            object_id=objid, axis=axis, direction=direction, delim=delim, position=end,
            color=color, cones=cones, callback=callback, move=move, parent=parent,
            private_userid=private_userid)

    def make_clickroot(self, objid, position, delim, rotation=None, move=False,
                       private_userid=None):
        if objid not in self.controls.keys():
            self.controls[objid] = {}
        name = f"{objid}{delim}clickroot"
        if rotation:
            name += "_rotated"
        else:
            rotation = Rotation(0, 0, 0, 1)
        if name not in self.controls[objid]:
            self.controls[objid][name] = Object(
                object_id=name,
                position=position,
                scale=Scale(arblib.SCL_CLICK, arblib.SCL_CLICK, arblib.SCL_CLICK),
                rotation=rotation,
                private_userid=private_userid,
            )
            self.scene.add_object(self.controls[objid][name])
        elif move:
            self.scene.update_object(self.controls[objid][name],
                                position=position, rotation=rotation)
        return name

    def do_move_relocate(self, camname, newposition):
        arblib.move_obj(self.scene, self.users[camname].target_id, newposition)
        self.users[camname].del_clipboard()

    # ------------------------------------------------------------------ #
    #  Increment helpers (static)                                          #
    # ------------------------------------------------------------------ #

    @staticmethod
    def incr_pos(coord, incr):
        div = round(coord / incr)
        res = (math.ceil(div) * incr) + incr
        return float('{0:g}'.format(res))

    @staticmethod
    def incr_neg(coord, incr):
        div = round(coord / incr)
        res = (math.floor(div) * incr) - incr
        return float('{0:g}'.format(res))

    @staticmethod
    def meters_increment(meters_style):
        if meters_style == "mm":
            return 0.001
        elif meters_style == "cm":
            return 0.01
        elif meters_style == "dm":
            return 0.1
        elif meters_style == "m":
            return 1.0

    # ------------------------------------------------------------------ #
    #  Clickline interaction callbacks                                     #
    # ------------------------------------------------------------------ #

    def nudgeline_callback(self, _scene, evt, msg):
        obj, direction, move, val = self.handle_clickline_event(evt, Mode.NUDGE)
        if not obj or not direction or "position" not in obj.data:
            return
        nudged = loc = obj.data.position
        if val == 0:
            inc = self.meters_increment(self.users[evt.object_id].target_style)
        else:
            inc = val
        if direction == "xp":
            nudged = Position(x=self.incr_pos(loc.x, inc), y=loc.y, z=loc.z)
        elif direction == "xn":
            nudged = Position(x=self.incr_neg(loc.x, inc), y=loc.y, z=loc.z)
        elif direction == "yp":
            nudged = Position(x=loc.x, y=self.incr_pos(loc.y, inc), z=loc.z)
        elif direction == "yn":
            nudged = Position(x=loc.x, y=self.incr_neg(loc.y, inc), z=loc.z)
        elif direction == "zp":
            nudged = Position(x=loc.x, y=loc.y, z=self.incr_pos(loc.z, inc))
        elif direction == "zn":
            nudged = Position(x=loc.x, y=loc.y, z=self.incr_neg(loc.z, inc))
        arblib.move_obj(self.scene, obj.object_id, nudged)
        print(f"{str(obj.data.position)} to {str(nudged)}")
        # always redraw nudgelines
        self.do_nudge_select(evt.object_id, obj.object_id, position=nudged)

    def scaleline_callback(self, _scene, evt, msg):
        obj, direction, move, val = self.handle_clickline_event(evt, Mode.SCALE)
        if not obj or not direction or "scale" not in obj.data:
            return
        scaled = sca = obj.data.scale
        if val == 0:
            inc = self.meters_increment(self.users[evt.object_id].target_style)
        else:
            inc = val
        if direction == "xp":
            scaled = Scale(x=self.incr_pos(sca.x, inc), y=self.incr_pos(
                sca.y, inc), z=self.incr_pos(sca.z, inc))
        elif direction == "xn":
            scaled = Scale(x=self.incr_neg(sca.x, inc), y=self.incr_neg(
                sca.y, inc), z=self.incr_neg(sca.z, inc))
        if scaled.x <= 0 or scaled.y <= 0 or scaled.z <= 0:
            return
        arblib.scale_obj(self.scene, obj.object_id, scaled)
        print(f"{str(obj.data.scale)} to {str(scaled)}")
        self.do_scale_select(evt.object_id, obj.object_id, scale=scaled)

    def stretchline_callback(self, _scene, evt, msg):
        obj, direction, move, val = self.handle_clickline_event(evt, Mode.STRETCH)
        if not obj or not direction or not move or "scale" not in obj.data or "position" not in obj.data:
            return
        scaled = sca = obj.data.scale
        moved = loc = obj.data.position
        if val == 0:
            inc = self.meters_increment(self.users[evt.object_id].target_style)
        else:
            inc = val
        if direction == "xp":
            scaled = Scale(x=self.incr_pos(sca.x, inc), y=sca.y, z=sca.z)
            moved = Position(x=self.recenter(
                scaled.x, sca.x, loc.x, move), y=loc.y, z=loc.z)
        elif direction == "xn":
            scaled = Scale(x=self.incr_neg(sca.x, inc), y=sca.y, z=sca.z)
            moved = Position(x=self.recenter(
                scaled.x, sca.x, loc.x, move), y=loc.y, z=loc.z)
        elif direction == "yp":
            scaled = Scale(x=sca.x, y=self.incr_pos(sca.y, inc), z=sca.z)
            moved = Position(x=loc.x, y=self.recenter(
                scaled.y, sca.y, loc.y, move), z=loc.z)
        elif direction == "yn":
            scaled = Scale(x=sca.x, y=self.incr_neg(sca.y, inc), z=sca.z)
            moved = Position(x=loc.x, y=self.recenter(
                scaled.y, sca.y, loc.y, move), z=loc.z)
        elif direction == "zp":
            scaled = Scale(x=sca.x, y=sca.y, z=self.incr_pos(sca.z, inc))
            moved = Position(x=loc.x, y=loc.y, z=self.recenter(
                scaled.z, sca.z, loc.z, move))
        elif direction == "zn":
            scaled = Scale(x=sca.x, y=sca.y, z=self.incr_neg(sca.z, inc))
            moved = Position(x=loc.x, y=loc.y, z=self.recenter(
                scaled.z, sca.z, loc.z, move))
        if scaled.x <= 0 or scaled.y <= 0 or scaled.z <= 0:
            return
        arblib.stretch_obj(self.scene, obj.object_id,
                           scale=scaled, position=moved)
        print(f"{str(obj.data.scale)} to {str(scaled)}")
        self.do_stretch_select(evt.object_id, obj.object_id, scale=scaled)

    def rotateline_callback(self, _scene, evt, msg):
        obj, direction, move, val = self.handle_clickline_event(evt, Mode.ROTATE)
        if not obj or not direction or "rotation" not in obj.data:
            return
        rotated = rot = obj.data.rotation
        if val == 0:
            inc = float(self.users[evt.object_id].target_style)
        else:
            inc = float(val)
        try:
            rot = arblib.rotation_quat2euler((rot.x, rot.y, rot.z, rot.w))
        except ValueError as error:
            print(f"Rotation error: {error}")
            return
        rot = (round(rot[0]), round(rot[1]), round(rot[2]))
        if direction == "xp":
            rotated = (self.incr_pos(rot[0], inc), rot[1], rot[2])
        elif direction == "xn":
            rotated = (self.incr_neg(rot[0], inc), rot[1], rot[2])
        elif direction == "yp":
            rotated = (rot[0], self.incr_pos(rot[1], inc), rot[2])
        elif direction == "yn":
            rotated = (rot[0], self.incr_neg(rot[1], inc), rot[2])
        elif direction == "zp":
            rotated = (rot[0], rot[1], self.incr_pos(rot[2], inc))
        elif direction == "zn":
            rotated = (rot[0], rot[1], self.incr_neg(rot[2], inc))
        if abs(rotated[0]) > 180 or abs(rotated[1]) > 180 or abs(rotated[2]) > 180:
            return
        try:
            rotated = arblib.rotation_euler2quat(rotated)
        except ValueError as error:
            print(f"Rotation error: {error}")
            return
        rotated = Rotation(x=rotated[0], y=rotated[1], z=rotated[2], w=rotated[3])
        arblib.rotate_obj(self.scene, obj.object_id, rotated)
        print(f"{str(obj.data.rotation)} to {str(rotated)}")
        self.do_rotate_select(evt.object_id, obj.object_id, rotation=rotated)

    @staticmethod
    def recenter(scaled, sca, loc, move):
        if move == "p_p" or move == "n_n":
            return loc + (abs(sca - scaled) / 2)
        else:
            return loc - (abs(sca - scaled) / 2)

    # ------------------------------------------------------------------ #
    #  Object creation                                                     #
    # ------------------------------------------------------------------ #

    def create_obj(self, camname, clipboard, position):
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
            clickable=True,  # FIXME: remove when AR target mousedown/up ignores parents
        )
        self.scene.add_object(new_obj)
        self.users[camname].target_id = new_obj.object_id
        print("Created " + new_obj.object_id)

    def clipboard_callback(self, _scene, evt, msg):
        camname = self.handle_clip_event(evt)
        if not camname:
            return
        targetPosition = evt.data.targetPosition
        originPosition = evt.data.originPosition
        if originPosition.x == 0 and originPosition.y == 0 and originPosition.z == 0:
            print('Invalid click position: event originPosition is uninitialized! Ignoring.')
            return
        if self.users[camname].mode == Mode.CREATE or self.users[camname].mode == Mode.MODEL:
            self.create_obj(camname, self.users[camname].get_clipboard(), targetPosition)
        elif self.users[camname].mode == Mode.MOVE:
            self.do_move_relocate(camname, targetPosition)

    # ------------------------------------------------------------------ #
    #  Wall creation                                                       #
    # ------------------------------------------------------------------ #

    def wall_callback(self, _scene, evt, msg):
        camname = self.handle_clip_event(evt)
        if not camname:
            return
        if not self.users[camname].wloc_start:
            self.do_wall_start(camname)
            self.users[camname].set_textright("End: tap opposing corner.")
        else:
            self.do_wall_end(camname)
            self.make_wall(camname)
            self.users[camname].wloc_start = self.users[camname].wloc_end = None  # reset
            self.users[camname].set_textright("Start: tap flush corner.")

    def do_wall_start(self, camname):
        # start (red)
        self.users[camname].wloc_start = self.users[camname].position
        self.users[camname].wrot_start = self.users[camname].rotation
        self.scene.add_object(arblib.temp_loc_marker(
            self.users[camname].wloc_start, arblib.CLR_WALL_START))
        self.scene.add_object(arblib.temp_rot_marker(self.users[camname].wloc_start,
                                                self.users[camname].wrot_start))

    def do_wall_end(self, camname):
        # end (green)
        self.users[camname].wloc_end = self.users[camname].position
        self.users[camname].wrot_end = self.users[camname].rotation
        self.scene.add_object(arblib.temp_loc_marker(
            self.users[camname].wloc_end, arblib.CLR_WALL_END))
        self.scene.add_object(arblib.temp_rot_marker(
            self.users[camname].wloc_end, self.users[camname].wrot_end))

    def make_wall(self, camname):
        # Wall theory: capture two poses and use them to place a wall object.
        # Also assumes first corner easier to capture accurate rotation than last.
        # Click 1: Capture the position and rotation.
        # Click 2: Capture the position only.
        sloc = self.users[camname].wloc_start
        eloc = self.users[camname].wloc_end
        srot = self.users[camname].wrot_start
        erot = self.users[camname].wrot_end
        print(f"S POS {str(sloc)}")
        print(f"E POS {str(eloc)}")
        # center point (blue)
        locx = statistics.median([sloc.x, eloc.x])
        locy = statistics.median([sloc.y, eloc.y])
        locz = statistics.median([sloc.z, eloc.z])
        pos = Position(locx, locy, locz)
        self.scene.add_object(arblib.temp_loc_marker(pos, arblib.CLR_WALL_CENTER))
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
        self.scene.add_object(arblib.temp_rot_marker(pos, rot))
        print(f"wall rotation {str(rot)}")
        # which axis to use for wall? use camera gaze
        # FIXME: wall rotation inference is still unreliable for non-axis-aligned gazes
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
            # ENHANCEMENT: add direction and hypotenuse for non-axis-parallel walls
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
            object_id=f"wall_{randstr}",
            position=pos,
            rotation=rot,
            scale=sca,
            material=Material(color=arblib.CLR_WALL,
                              transparent=True, opacity=arblib.OPC_TRANSLUCENT),
            clickable=True,  # FIXME: remove when AR target mousedown/up ignores parents
        )
        self.scene.add_object(new_wall)
        self.users[camname].target_id = new_wall.object_id
        print(f"Created {new_wall.object_id} r{str(rot)} s{str(sca)}")
        # ENHANCEMENT: remove wall opacity in final wall feature
        # ENHANCEMENT: push wall front side flush with markers (position-(wall/2))

    # ------------------------------------------------------------------ #
    #  Main scene callback (MQTT message handler)                          #
    # ------------------------------------------------------------------ #

    def scene_callback(self, _scene, obj, msg):
        # This is the MQTT message callback function for the scene
        object_type = None
        if "data" in msg and "object_type" in msg["data"]:
            object_type = msg["data"]["object_type"]

        if object_type == "camera":
            # camera updates define users present
            camname = obj.object_id
            if camname not in self.users:
                return  # wait for user_join_callback

            # save camera's attitude in the world
            self.users[camname].position_last = self.users[camname].position
            self.users[camname].rotation_last = self.users[camname].rotation
            self.users[camname].position = Position(msg["data"]["position"]["x"],
                                               msg["data"]["position"]["y"],
                                               msg["data"]["position"]["z"])
            self.users[camname].rotation = Rotation(msg["data"]["rotation"]["x"],
                                               msg["data"]["rotation"]["y"],
                                               msg["data"]["rotation"]["z"],
                                               msg["data"]["rotation"]["w"])


            # floating controller — position panel on a sphere around the camera
            # Compute camera yaw/pitch directly from the quaternion's forward
            # vector to avoid gimbal lock in Euler XYZ decomposition (rx flips
            # by ±π when yaw approaches ±90°, corrupting lock offsets)
            qx = msg["data"]["rotation"]["x"]
            qy = msg["data"]["rotation"]["y"]
            qz = msg["data"]["rotation"]["z"]
            qw = msg["data"]["rotation"]["w"]

            # Camera yaw: horizontal look direction from forward vector
            # projected onto XZ plane. Stable full [-π, π] range.
            camera_yaw = math.atan2(
                2 * (qx * qz + qw * qy),
                1 - 2 * (qx * qx + qy * qy))

            # Camera pitch: vertical look angle from forward vector Y component.
            # Clamped to [-π/2, π/2] — stable, no gimbal coupling.
            sinp = 2 * (qw * qx - qy * qz)
            camera_pitch = math.copysign(math.pi / 2, sinp) if abs(sinp) >= 1 else math.asin(sinp)

            if not self.users[camname].follow_lock:
                # First frame after unlock: compute cumulative offset so
                # the panel appears not to move from its locked position
                if self.users[camname].lock_on_ry is not None:
                    delta_yaw = camera_yaw - self.users[camname].lock_on_ry
                    delta_pitch = camera_pitch - self.users[camname].lock_on_rx
                    # Normalize yaw delta to [-π, π] for wrap-around
                    delta_yaw = math.atan2(math.sin(delta_yaw), math.cos(delta_yaw))
                    self.users[camname].lock_ry += delta_yaw
                    self.users[camname].lock_rx += delta_pitch
                    self.users[camname].lock_on_ry = None
                    self.users[camname].lock_on_rx = None

                # Spherical coordinates with offset:
                #   azimuth (horizontal) derived from camera yaw
                #   inclination (vertical) derived from camera pitch
                #   lock_ry/lock_rx store cumulative angular offsets from lock toggles
                azi = (math.pi / 2) - camera_yaw + self.users[camname].lock_ry
                inc = (math.pi / 2) + camera_pitch - self.users[camname].lock_rx

                # Spherical to Cartesian (r, azi, inc) → (x, y, z)
                px = arblib.PANEL_RADIUS * math.cos(azi) * math.sin(inc)
                py = arblib.PANEL_RADIUS * math.cos(inc)
                pz = -(arblib.PANEL_RADIUS * math.sin(azi) * math.sin(inc))
                self.scene.update_object(
                    self.users[camname].follow, position=Position(px, py, pz))
            else:
                # Lock is ON: save camera yaw/pitch once (first locked frame)
                # to compute the delta when lock is released
                if self.users[camname].lock_on_ry is None:
                    self.users[camname].lock_on_ry = camera_yaw
                    self.users[camname].lock_on_rx = camera_pitch


            # handle gesturing two-finger touch as clickline camera match-moves
            if self.users[camname].gesturing and not self.users[camname].slider:
                if self.users[camname].mode == Mode.NUDGE:
                    self.nudgeline_callback(_scene, obj, msg)
                elif self.users[camname].mode == Mode.ROTATE:
                    self.rotateline_callback(_scene, obj, msg)
                elif self.users[camname].mode == Mode.SCALE:
                    self.scaleline_callback(_scene, obj, msg)
                elif self.users[camname].mode == Mode.STRETCH:
                    self.stretchline_callback(_scene, obj, msg)

        # mouse event
        elif getattr(obj, "action", None) == "clientEvent":
            # v2 migration: object_id is now the user, target is the clicked object
            camname = msg["object_id"]
            object_id = msg.get("data", {}).get("target", camname)
            evt_type = msg.get("type", "")  # save event type before obj may be overwritten
            if camname not in self.users:
                return  # wait for user_join_callback

            # only persisted objects should handle clicks
            if object_id in _scene.all_objects:
                scene_obj = _scene.all_objects[object_id]
                if not scene_obj.persist:
                    return

            # show objects with events
            if evt_type == EVT_MOUSEENTER:
                if self.users[camname].redpill:
                    self.show_redpill_obj(camname, object_id)
                else:
                    self.users[camname].set_textstatus(object_id)
            elif evt_type == EVT_MOUSELEAVE:
                self.users[camname].set_textstatus("")

            # handle click
            elif evt_type == EVT_MOUSEDOWN:
                # clicked on persisted object to modify
                self.update_controls(self.users[camname].target_id)
                self.users[camname].target_id = object_id  # always update
                if self.users[camname].mode == Mode.DELETE:
                    arblib.delete_obj(self.scene, object_id)
                elif self.users[camname].mode == Mode.MOVE:
                    self.do_move_select(camname, object_id)
                elif self.users[camname].mode == Mode.NUDGE:
                    self.do_nudge_select(camname, object_id)
                elif self.users[camname].mode == Mode.SCALE:
                    self.do_scale_select(camname, object_id)
                elif self.users[camname].mode == Mode.STRETCH:
                    self.do_stretch_select(camname, object_id)
                elif self.users[camname].mode == Mode.ROTATE:
                    self.do_rotate_select(camname, object_id)
                elif self.users[camname].mode == Mode.COLOR:
                    arblib.color_obj(self.scene, object_id,
                                     Color(self.users[camname].target_style))
                elif self.users[camname].mode == Mode.OCCLUDE:
                    arblib.occlude_obj(self.scene, object_id,
                                       self.users[camname].target_style)
                elif self.users[camname].mode == Mode.RENAME or self.users[camname].mode == Mode.PARENT:
                    if len(self.users[camname].typetext) > 0:  # edits already made
                        new_id = self.users[camname].typetext
                        self.users[camname].typetext = ""
                        if self.users[camname].mode == Mode.PARENT:
                            arblib.parent_obj(self.scene, object_id, new_id)
                        else:
                            self.do_rename(camname, object_id, new_id)
                    else:  # no edits yet, load previous name to change
                        self.users[camname].typetext = object_id
                    self.users[camname].set_textright(self.users[camname].typetext)

            # handle two-finger touch as clickline sliders
            elif evt_type == "twofingerstart" or evt_type == "twofingermove" or evt_type == "twofingerend":
                if self.users[camname].mode == Mode.NUDGE:
                    self.nudgeline_callback(_scene, obj, msg)
                elif self.users[camname].mode == Mode.ROTATE:
                    self.rotateline_callback(_scene, obj, msg)
                elif self.users[camname].mode == Mode.SCALE:
                    self.scaleline_callback(_scene, obj, msg)
                elif self.users[camname].mode == Mode.STRETCH:
                    self.stretchline_callback(_scene, obj, msg)

            # handle three-finger touch as toggle for clickline modes
            elif evt_type == "threefingerstart":
                if self.users[camname].mode == Mode.NONE:
                    buttonname = Mode.ROTATE
                elif self.users[camname].mode == Mode.ROTATE:
                    buttonname = Mode.NUDGE
                elif self.users[camname].mode == Mode.NUDGE:
                    buttonname = Mode.SCALE
                elif self.users[camname].mode == Mode.SCALE:
                    buttonname = Mode.STRETCH
                else:
                    buttonname = self.users[camname].mode  # collapse
                obj = Event(  # convert to panel click
                    object_id=f"{camname}_button_{buttonname.value}",
                    action="clientEvent",
                    type=EVT_MOUSEDOWN,
                    data={"source": camname})
                self.panel_callback(_scene, obj, msg)

    # ------------------------------------------------------------------ #
    #  Lifecycle                                                           #
    # ------------------------------------------------------------------ #

    def end_program_callback(self, _scene):
        for camname in list(self.users.keys()):
            # clean up per-user redpill objects
            for obj_id in self.users[camname].redpill_objects:
                arblib.delete_obj(self.scene, obj_id)
            self.users[camname].delete()
        for objid in self.controls:
            for ctrl in self.controls[objid]:
                _scene.delete_object(self.controls[objid][ctrl])


if __name__ == "__main__":
    app = ArbApp()
    app.run()
