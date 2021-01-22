from ..utils import Utils
from .attribute import Attribute
from .position import Position

class Impulse(Attribute):
    """
    Impulse Attribute.
    Usage: impulse=Impulse(...)
    """
    def __init__(self, on="mousedown", force=Position(0,0,0), position=Position(0,0,0)):
        if isinstance(force, Position):
            force = force.to_str()
        elif isinstance(force, tuple) or isinstance(force, list):
            force = Utils.tuple_to_string(force)

        if isinstance(position, Position):
            position = position.to_str()
        elif isinstance(position, tuple) or isinstance(position, list):
            position = Utils.tuple_to_string(position)

        super().__init__(on=on, force=force, position=position)
