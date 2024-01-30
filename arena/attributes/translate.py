# This file is auto-generated from github.com/arenaxr/arena-schema, changes here may be overwritten.

from .animation import *
from .animation_mixer import *
from .armarker import *
from .attribution import *
from .blip import *
from .box_collision_listener import *
from .click_listener import *
from .dynamic_body import *
from .gltf_model_lod import *
from .gltf_morph import *
from .goto_landmark import *
from .goto_url import *
from .impulse import *
from .jitsi_video import *
from .landmark import *
from .material import *
from .material_extras import *
from .model_update import *
from .multisrc import *
from .position import *
from .remote_render import *
from .rotation import *
from .scale import *
from .shadow import *
from .sound import *
from .spe_particles import *
from .static_body import *
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
    "dynamic_body": "dynamic-body",
    "gltf_model_lod": "gltf-model-lod",
    "gltf_morph": "gltf-morph",
    "goto_landmark": "goto-landmark",
    "goto_url": "goto-url",
    "hide_on_enter_ar": "hide-on-enter-ar",
    "hide_on_enter_vr": "hide-on-enter-vr",
    "impulse": "impulse",
    "jitsi_video": "jitsi-video",
    "landmark": "landmark",
    "look_at": "look-at",
    "material": "material",
    "material_extras": "material-extras",
    "modelUpdate": "modelUpdate",
    "multisrc": "multisrc",
    "parent": "parent",
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
    "static_body": "static-body",
    "textinput": "textinput",
    "url": "url",
    "video_control": "video-control",
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
    "dynamic-body": "dynamic_body",
    "gltf-model-lod": "gltf_model_lod",
    "gltf-morph": "gltf_morph",
    "goto-landmark": "goto_landmark",
    "goto-url": "goto_url",
    "hide-on-enter-ar": "hide_on_enter_ar",
    "hide-on-enter-vr": "hide_on_enter_vr",
    "impulse": "impulse",
    "jitsi-video": "jitsi_video",
    "landmark": "landmark",
    "look-at": "look_at",
    "material": "material",
    "material-extras": "material_extras",
    "modelUpdate": "modelUpdate",
    "multisrc": "multisrc",
    "parent": "parent",
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
    "static-body": "static_body",
    "textinput": "textinput",
    "url": "url",
    "video-control": "video_control",
}

ATTRIBUTE_CLASS_TRANSLATION = {
    "animation": Animation,
    "animation_mixer": AnimationMixer,
    "armarker": Armarker,
    "attribution": Attribution,
    "blip": Blip,
    "box_collision_listener": BoxCollisionListener,
    "click_listener": ClickListener,
    "dynamic_body": DynamicBody,
    "gltf_model_lod": GltfModelLod,
    "gltf_morph": GltfMorph,
    "goto_landmark": GotoLandmark,
    "goto_url": GotoUrl,
    "impulse": Impulse,
    "jitsi_video": JitsiVideo,
    "landmark": Landmark,
    "material": Material,
    "material_extras": MaterialExtras,
    "modelUpdate": ModelUpdate,
    "multisrc": Multisrc,
    "position": Position,
    "remote_render": RemoteRender,
    "rotation": Rotation,
    "scale": Scale,
    "shadow": Shadow,
    "sound": Sound,
    "spe_particles": SpeParticles,
    "static_body": StaticBody,
    "textinput": Textinput,
    "video_control": VideoControl,
}
