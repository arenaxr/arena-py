from .animation_mixer import AnimationMixer
from .animation import Animation
from .attribute import Attribute
from .color import Color
from .data import Data
from .goto_url import GotoUrl
from .impulse import Impulse
from .material import Material
from .morph import Morph
from .physics import Physics
from .position import Position
from .rotation import Rotation
from .scale import Scale
from .sound import Sound
from .text_input import TextInput

# [TODO]: do something with this
ATTRIBUTE_TYPE_MAP = {
    "animation-mixer": AnimationMixer,
    "animation": Animation,
    "attribute": Attribute,
    "color": Color,
    "data": Data,
    "goto_url": GotoUrl,
    "impulse": Impulse,
    "material": Material,
    "morph": Morph,
    "physics": Physics,
    "position": Position,
    "rotation": Rotation,
    "scale": Scale,
    "sound": Sound,
}
