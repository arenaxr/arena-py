from .arena_object import Object

class Text(Object):
    """
    Class for Text in the ARENA.
    [TODO]: update_attribute(text="new text") does get published. maybe a client-side issue?
    """
    def __init__(self, text="placeholder text", **kwargs):
        super().__init__(object_type="text", text=text, **kwargs)
