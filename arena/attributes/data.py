from ..utils import *
from .attribute import Attribute
from .color import Color
from .dynamic_body import Physics
from .goto_url import GotoUrl
from .jitsi_video import JitsiVideo
from .material import Material
from .position import Position
from .rotation import Rotation
from .scale import Scale
from .translate import ATTRIBUTE_CLASS_TRANSLATION, KEYWORD_ATTRIBUTE_TRANSLATION
from .video_control import VideoControl


class Data(Attribute):
    """
    Data attribute class to manage its properties in the ARENA: Wraps all attributes in JSON.
    Usage: `data=Data(...)`

    :param dict animation: Animate and tween values. More properties at <https://aframe.io/docs/1.5.0/components/animation.html> A-Frame Animation component. Easing properties are detailed at <https://easings.net> easings.net. (optional)
    :param dict animation_mixer: A list of available animations can usually be found by inspecting the model file or its documentation. All animations will play by default. To play only a specific set of animations, use wildcards: animation-mixer='clip: run_*'. Requires `object_type: gltf-model`. More properties at <https://github.com/n5ro/aframe-extras/tree/master/src/loaders#animation> A-Frame Extras Animation. (optional)
    :param dict armarker: A location marker (such as an AprilTag, a lightAnchor, or an UWB tag), used to anchor scenes, or scene objects, in the real world. (optional)
    :param dict attribution: Attribution Component. Saves attribution data in any entity. (optional)
    :param dict blip: When the object is created or deleted, it will animate in/out of the scene instead of appearing/disappearing instantly. Must have a geometric mesh. (optional)
    :param dict box_collision_listener: Listen for bounding-box collisions with user camera and hands. Must be applied to an object or model with geometric mesh. Collisions are determined by course bounding-box overlaps. (optional)
    :param bool buffer: Transform geometry into a BufferGeometry to reduce memory usage at the cost of being harder to manipulate (geometries only: box, circle, cone, ...). Defaults to 'True' (optional)
    :param dict click_listener: Object will listen for mouse events like clicks. (optional)
    :param str collision_listener: Name of the collision-listener, default can be empty string. Collisions trigger click events. Requires `scene-options: physics`. (optional)
    :param str color: ***DEPRECATED**: data.color is **deprecated** for primitive geometry, use data.material.color instead.* (deprecated)
    :param dict dynamic_body: ***DEPRECATED**: data.dynamic-body is **deprecated**, use data.physx-body instead.* (deprecated)
    :param dict gltf_model_lod: Simple switch between the default gltf-model and a detailed one when a user camera is within specified distance. Requires `object_type: gltf-model`. (optional)
    :param dict gltf_morph: Allows you to target and control a gltf model's morphTargets created in Blender. Requires `object_type: gltf-model`. More properties at <https://github.com/elbobo/aframe-gltf-morph-component> A-Frame GLTF Morph component. (optional)
    :param dict goto_landmark: Teleports user to the landmark with the given name. Requires `click-listener` attribute. (optional)
    :param dict goto_url: Load new URL when object is clicked. Requires `click-listener` attribute. (optional)
    :param bool hide_on_enter_ar: Hide object when entering AR. Remove component to *not* hide. (optional)
    :param bool hide_on_enter_vr: Hide object when entering VR. Remove component to *not* hide. (optional)
    :param dict impulse: ***DEPRECATED**: data.impulse is **deprecated**, use data.physx-force-pushable instead.* (deprecated)
    :param dict jitsi_video: Apply a jitsi video source to the geometry. (optional)
    :param dict landmark: Define entities as a landmark; Landmarks appears in the landmark list and you can move (teleport) to them; You can define the behavior of the teleport: if you will be at a fixed or random distance, looking at the landmark, fixed offset or if it is constrained by a navmesh (when it exists). (optional)
    :param str look_at: The look-at component defines the behavior for an entity to dynamically rotate or face towards another entity or position. Use '#my-camera' to face the user camera, otherwise can take either a vec3 position or a query selector to another entity. (optional)
    :param dict material: The material properties of the object's surface. More properties at <https://aframe.io/docs/1.5.0/components/material.html> A-Frame Material. (optional)
    :param dict material_extras: Define extra material properties, namely texture encoding, whether to render the material's color and render order. Requires `material` attribute. More properties at <https://threejs.org/docs/#api/en/materials/Material> THREE.js Material. (optional)
    :param dict model_container: Overrides absolute size for a 3D model. The model can be a glTF, glb, obj, or any other supported format. The model will be rescaled to fit to the sizes specified for each axes. (optional)
    :param dict modelUpdate: The GLTF-specific `modelUpdate` attribute is an object with child component names as keys. The top-level keys are the names of the child components to be updated. The values of each are nested `position` and `rotation` attributes to set as new values, respectively. Either `position` or `rotation` can be omitted if unchanged. Requires `object_type: gltf-model`. (optional)
    :param dict multisrc: Define multiple visual sources applied to an object. Requires `material` attribute. (optional)
    :param str parent: Parent's object_id. Child objects inherit attributes of their parent, for example scale and translation. (optional)
    :param dict physx_body: Turns an entity into a PhysX rigid body. This is the main component for creating physics objects. There are 3 types of rigid bodies: dynamic objects that have physics simulated on them, static objects that cannot move, and kinematic objects that can be moved programmatically but not by simulation. Requires `scene-options: physics`. (optional)
    :param dict physx_force_pushable: Makes a physx-body object pushable by the user. Requires `click-listener` attribute. Requires `scene-options: physics`. (optional)
    :param bool physx_grabbable: Makes a physx-body object grabbable by the user's hands. Requires `scene-options: physics`. Defaults to 'True' (optional)
    :param dict physx_joint: Creates a PhysX joint between an ancestor rigid body and a target rigid body. Position and rotation of the entity will be used to create the corresponding joint. Requires `scene-options: physics`. (optional)
    :param dict physx_joint_constraint: Adds a constraint to a physx-joint. Supported joints are D6, Revolute and Prismatic. Can only be used on an entity with the physx-joint component. Requires `scene-options: physics`. (optional)
    :param dict physx_joint_driver: Creates a driver which exerts force to return the joint to the initial position with the given velocity characteristics. Can only be used on an entity with a physx-joint component. Currently only supports D6 joint type. Requires `scene-options: physics`. (optional)
    :param dict physx_material: Controls physics properties for individual shapes or rigid bodies. Can be set on an entity with physx-body or on shapes contained within it. Requires `scene-options: physics`. (optional)
    :param dict position: 3D object position. (optional)
    :param dict remote_render: Whether or not an object should be remote rendered [Experimental]. (optional)
    :param dict rotation: 3D object rotation in quaternion representation; Right-handed coordinate system. Euler degrees are **deprecated** in wire message format. (optional)
    :param dict scale: 3D object scale. (optional)
    :param bool screenshareable: Whether or not a user can screenshare on an object. Defaults to 'True' (optional)
    :param dict shadow: The shadow component enables shadows for an entity and its children. Adding the shadow component alone is not enough to display shadows in your scene. We must have at least one light with castShadow: true enabled. (optional)
    :param bool show_on_enter_ar: Show object when entering AR. Hidden otherwise. (optional)
    :param bool show_on_enter_vr: Show object when entering VR. Hidden otherwise. (optional)
    :param bool skipCache: Disable retrieving the shared geometry object from the cache. (geometries only: box, circle, cone, ...). Defaults to 'False' (optional)
    :param dict sound: The sound component defines the entity as a source of sound or audio. The sound component can be positional and is thus affected by the component's position. More properties at <https://aframe.io/docs/1.5.0/components/sound.html> A-Frame Sound. (optional)
    :param dict spe_particles: GPU based particle systems in A-Frame. More properties at <https://github.com/harlyq/aframe-spe-particles-component> A-Frame SPE Particles component. (optional)
    :param dict static_body: ***DEPRECATED**: data.static-body is **deprecated**, use data.physx-body instead.* (deprecated)
    :param str submodel_parent: When this object is parented to a hierarchical model, it attaches to a named sub-component of that model instead of the root position. Requires `parent` attribute. Defaults to '' (optional)
    :param dict textinput: Opens an HTML prompt when clicked. Sends text input as an event on MQTT. Requires `click-listener` attribute. (optional)
    :param str url: Use File Store paths under 'store/users/username', see CDN and other storage options in the description above. (optional)
    :param dict video_control: Adds a video to an entity and controls its playback. (optional)
    :param bool visible: Whether object is visible. Property is inherited. Defaults to 'True' (optional)
    """
    def __init__(self, **kwargs):
        data = {}
        data = Data.update_data(data, kwargs)
        super().__init__(**data)

    @classmethod
    def update_data(cls, data, new_data):
        new_data = new_data.get("data", new_data)
        dash_words = []
        for k, v in new_data.items():

            # when value is None, do not parse it
            if v is None:
                data[k] = v
                continue

            # If the value is another Arena Object besides parent, this is not valid.
            # Crude check that avoids circular import of Arena Object.
            if v.__class__.__bases__[0].__name__ == "Object" and k != 'parent':
                raise ValueError(f"Invalid Arena Object as attribute {k}: {v.object_id}")

            # allow user to input tuples, lists, dicts, etc for specific Attributes.
            # everything gets converted to corresponding attribute
            if (k == "position" or k == "start" or k == "end") and not isinstance(v, Position):
                if isinstance(v, (list, tuple)):
                    data[k] = Position(*v[:3])
                elif isinstance(v, dict):
                    data[k] = Position(**v)
                elif isinstance(v, str):
                    data[k] = Position(v)
                else:
                    data[k] = v

            elif k == "rotation" and not isinstance(v, Rotation):
                if isinstance(v, (list, tuple)):
                    if len(v) == 3:
                        data[k] = Rotation(*v[:3], None)
                    else:
                        data[k] = Rotation(*v[:4])
                elif isinstance(v, dict):
                    data[k] = Rotation(**v)
                elif isinstance(v, str):
                    data[k] = Rotation(v)
                else:
                    data[k] = v

            elif k == "scale" and not isinstance(v, Scale):
                if isinstance(v, (list, tuple)):
                    data[k] = Scale(*v[:3])
                elif isinstance(v, dict):
                    data[k] = Scale(**v)
                elif isinstance(v, str):
                    data[k] = Scale(v)
                else:
                    data[k] = v

            elif k == "color" and not isinstance(v, Color):
                if isinstance(v, (list, tuple)):
                    color = Color(*v[:3])
                elif isinstance(v, dict):
                    color = Color(**v)
                elif isinstance(v, str):
                    color = Color(v)
                else:
                    color = v
                data[k] = color

            elif k == "material":
                if "color" in v:
                    color = v["color"]
                    if isinstance(color, (list, tuple)):
                        color = Color(*color[:3])
                    elif isinstance(color, dict):
                        color = Color(**color)
                    elif isinstance(color, str):
                        color = Color(color)
                    else:
                        color = v["color"]
                    v["color"] = color
                if isinstance(v, dict):
                    data[k] = Material(**v)
                else:
                    data[k] = v

            # Translate and handle underscores from any other keys.
            # Must be done last since KEYWORD_ATTRIBUTE_TRANSLATION contains all attributes,
            # which may interfere with special casing above from, say "rotation" for example.
            elif k in KEYWORD_ATTRIBUTE_TRANSLATION:
                if "-" in k:
                    dash_words += [k]
                    k = KEYWORD_ATTRIBUTE_TRANSLATION[k]
                if isinstance(v, dict):
                    data[k] = ATTRIBUTE_CLASS_TRANSLATION[k](**v)
                else:
                    data[k] = v

            elif isinstance(v, Attribute):
                data[k] = v

            else:
                try:
                    # unknown attribute
                    data[k] = Attribute(**v)
                except:
                    data[k] = v

            # make False into None
            if (isinstance(v, bool) and v == False) or v is None:
                data[k] = None

        # delete elements with keys that have dashes
        for w in dash_words:
            if w in data:
                del data[w]

        return data
