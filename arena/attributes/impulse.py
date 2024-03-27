from ..utils import Utils
from .attribute import Attribute
from .position import Position

class Impulse(Attribute):
    """
    Impulse attribute class to manage its properties in the ARENA: Apply an impulse to an object to set it in motion. This happens in conjunction with an event. Requires click-listener and physics.
    Usage: `impulse=Impulse(...)`

    :param dict force: Impulse vector. Defaults to '{'x': 1, 'y': 1, 'z': 1}' (optional)
    :param str on: Event to listen 'on'. Allows [mousedown, mouseup] Defaults to 'mousedown' (optional)
    :param dict position: World position. Defaults to '{'x': 1, 'y': 1, 'z': 1}' (optional)
    """
    def __init__(self, on="mousedown", force=Position(0,0,0), position=Position(0,0,0), **kwargs):
        if isinstance(force, Position):
            force = force.to_str()
        elif isinstance(force, tuple) or isinstance(force, list):
            force = Utils.tuple_to_string(force)

        if isinstance(position, Position):
            position = position.to_str()
        elif isinstance(position, tuple) or isinstance(position, list):
            position = Utils.tuple_to_string(position)

        super().__init__(on=on, force=force, position=position, **kwargs)
