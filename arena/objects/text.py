from .arena_object import Object

class Text(Object):
    """
    Class for Text in the ARENA.
    """
    object_type = "text"

    def __init__(self, text="placeholder text", **kwargs):
        super().__init__(object_type=Text.object_type, text=text, **kwargs)
