# This file is auto-generated from github.com/arenaxr/arena-schema, changes here may be overwritten.

from .animation import *
from .animation_mixer import *
from .armarker import *
from .attribution import *
from .blip import *
from .box_collision_listener import *
from .click_listener import *
from .gltf_model_lod import *
from .gltf_morph import *
from .goto_landmark import *
from .goto_url import *
from .jitsi_video import *
from .landmark import *
from .material import *
from .material_extras import *
from .model_container import *
from .model_update import *
from .multisrc import *
from .physx_body import *
from .physx_force_pushable import *
from .physx_joint import *
from .physx_joint_constraint import *
from .physx_joint_driver import *
from .physx_material import *
from .position import *
from .remote_render import *
from .rotation import *
from .scale import *
from .shadow import *
from .sound import *
from .spe_particles import *
from .textinput import *
from .video_control import *

ATTRIBUTE_KEYWORD_TRANSLATION = {
    "physics": "dynamic-body",  # backward-compatibility
    "clickable": "click-listener",  # backward-compatibility
    "animation": "animation",
    "animation_mixer": "animation-mixer",
    "armarker": "armarker",
    "attribution": "attribution",
    "blip": "blip",
    "box_collision_listener": "box-collision-listener",
    "buffer": "buffer",
    "click_listener": "click-listener",
    "collision_listener": "collision-listener",
    "gltf_model_lod": "gltf-model-lod",
    "gltf_morph": "gltf-morph",
    "goto_landmark": "goto-landmark",
    "goto_url": "goto-url",
    "hide_on_enter_ar": "hide-on-enter-ar",
    "hide_on_enter_vr": "hide-on-enter-vr",
    "jitsi_video": "jitsi-video",
    "landmark": "landmark",
    "look_at": "look-at",
    "material": "material",
    "material_extras": "material-extras",
    "model_container": "model-container",
    "modelUpdate": "modelUpdate",
    "multisrc": "multisrc",
    "parent": "parent",
    "physx_body": "physx-body",
    "physx_force_pushable": "physx-force-pushable",
    "physx_grabbable": "physx-grabbable",
    "physx_joint": "physx-joint",
    "physx_joint_constraint": "physx-joint-constraint",
    "physx_joint_driver": "physx-joint-driver",
    "physx_material": "physx-material",
    "position": "position",
    "remote_render": "remote-render",
    "rotation": "rotation",
    "scale": "scale",
    "screenshareable": "screenshareable",
    "shadow": "shadow",
    "show_on_enter_ar": "show-on-enter-ar",
    "show_on_enter_vr": "show-on-enter-vr",
    "skipCache": "skipCache",
    "sound": "sound",
    "spe_particles": "spe-particles",
    "submodel_parent": "submodel-parent",
    "textinput": "textinput",
    "url": "url",
    "video_control": "video-control",
    "visible": "visible",
}

KEYWORD_ATTRIBUTE_TRANSLATION = {
    "animation": "animation",
    "animation-mixer": "animation_mixer",
    "armarker": "armarker",
    "attribution": "attribution",
    "blip": "blip",
    "box-collision-listener": "box_collision_listener",
    "buffer": "buffer",
    "click-listener": "click_listener",
    "collision-listener": "collision_listener",
    "gltf-model-lod": "gltf_model_lod",
    "gltf-morph": "gltf_morph",
    "goto-landmark": "goto_landmark",
    "goto-url": "goto_url",
    "hide-on-enter-ar": "hide_on_enter_ar",
    "hide-on-enter-vr": "hide_on_enter_vr",
    "jitsi-video": "jitsi_video",
    "landmark": "landmark",
    "look-at": "look_at",
    "material": "material",
    "material-extras": "material_extras",
    "model-container": "model_container",
    "modelUpdate": "modelUpdate",
    "multisrc": "multisrc",
    "parent": "parent",
    "physx-body": "physx_body",
    "physx-force-pushable": "physx_force_pushable",
    "physx-grabbable": "physx_grabbable",
    "physx-joint": "physx_joint",
    "physx-joint-constraint": "physx_joint_constraint",
    "physx-joint-driver": "physx_joint_driver",
    "physx-material": "physx_material",
    "position": "position",
    "remote-render": "remote_render",
    "rotation": "rotation",
    "scale": "scale",
    "screenshareable": "screenshareable",
    "shadow": "shadow",
    "show-on-enter-ar": "show_on_enter_ar",
    "show-on-enter-vr": "show_on_enter_vr",
    "skipCache": "skipCache",
    "sound": "sound",
    "spe-particles": "spe_particles",
    "submodel-parent": "submodel_parent",
    "textinput": "textinput",
    "url": "url",
    "video-control": "video_control",
    "visible": "visible",
}

ATTRIBUTE_CLASS_TRANSLATION = {
    "animation": Animation,
    "animation_mixer": AnimationMixer,
    "armarker": Armarker,
    "attribution": Attribution,
    "blip": Blip,
    "box_collision_listener": BoxCollisionListener,
    "click_listener": ClickListener,
    "gltf_model_lod": GltfModelLod,
    "gltf_morph": GltfMorph,
    "goto_landmark": GotoLandmark,
    "goto_url": GotoUrl,
    "jitsi_video": JitsiVideo,
    "landmark": Landmark,
    "material": Material,
    "material_extras": MaterialExtras,
    "model_container": ModelContainer,
    "modelUpdate": ModelUpdate,
    "multisrc": Multisrc,
    "physx_body": PhysxBody,
    "physx_force_pushable": PhysxForcePushable,
    "physx_joint": PhysxJoint,
    "physx_joint_constraint": PhysxJointConstraint,
    "physx_joint_driver": PhysxJointDriver,
    "physx_material": PhysxMaterial,
    "position": Position,
    "remote_render": RemoteRender,
    "rotation": Rotation,
    "scale": Scale,
    "shadow": Shadow,
    "sound": Sound,
    "spe_particles": SpeParticles,
    "textinput": Textinput,
    "video_control": VideoControl,
}
