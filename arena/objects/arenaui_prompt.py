from .arena_object import Object


class ArenauiPrompt(Object):
    """
    Popup Prompt in the ARENA UI.

    :param str title: Title of Prompt (optional)
    :param str description: Additional desc text of prompt (optional)
    :param list[str] buttons: List of button name strings (optional)
    :param str width: Width of prompt (optional)
    :param str font: Font of button panel ['Roboto', 'Roboto-Mono'] (optional)
    """
    object_type = "arenaui-prompt"

    def __init__(self, **kwargs):
        super().__init__(object_type=ArenauiPrompt.object_type, **kwargs)


class Prompt(ArenauiPrompt):
    """
    Alternate name for ArenauiPrompt.
    """
