from .arena_object import Object

class ArenauiPrompt(Object):
    """
    ArenauiPrompt object class to manage its properties in the ARENA: ARENAUI element which displays prompt with button actions.

    :param list[str] buttons: Buttons Defaults to '['Confirm', 'Cancel']' (optional)
    :param str description: Description Defaults to 'This is a prompt. Please confirm or cancel.' (optional)
    :param str font: Font to use for button text. Allows [Roboto, Roboto-Mono] Defaults to 'Roboto' (optional)
    :param str materialSides: Which sides display the rendered UI material Allows [both, front] Defaults to 'both' (optional)
    :param str theme: Color Theme Allows [light, dark] Defaults to 'light' (optional)
    :param str title: Title Defaults to 'Prompt' (optional)
    :param float width: Override width Defaults to '1.5' (optional)
    """
    object_type = "arenaui-prompt"

    def __init__(self, **kwargs):
        super().__init__(object_type=ArenauiPrompt.object_type, **kwargs)


class Prompt(ArenauiPrompt):
    """
    Alternate name for ArenauiPrompt.
    """
