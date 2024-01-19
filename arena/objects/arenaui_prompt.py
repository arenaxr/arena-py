from .arena_object import Object

class ArenauiPrompt(Object):
    """
    ArenauiPrompt object class to manage its properties in the ARENA: ARENAUI element which displays prompt with button actions.
    
    :param str title: Title; defaults to 'Prompt' (optional)
    :param str description: Description; defaults to 'This is a prompt. Please confirm or cancel.' (optional)
    :param list[str] buttons: Buttons; defaults to '['Confirm', 'Cancel']' (optional)
    :param float width: Override width; defaults to '1.5' (optional)
    :param str font: Font to use for button text [Roboto, Roboto-Mono]; defaults to 'Roboto' (optional)
    :param str theme: Color Theme [light, dark]; defaults to 'light' (optional)
    """
    object_type = "arenaui-prompt"

    def __init__(self, **kwargs):
        super().__init__(object_type=ArenauiPrompt.object_type, **kwargs)


class Prompt(ArenauiPrompt):
    """
    Alternate name for ArenauiPrompt.
    """
