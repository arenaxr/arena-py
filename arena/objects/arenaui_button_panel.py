from .arena_object import Object

class ArenauiButtonPanel(Object):
    """
    ArenauiButtonPanel object class to manage its properties in the ARENA: ARENAUI element which displays a vertical or horizontal panel of buttons.

    :param list[dict] buttons: Buttons Defaults to '[{'name': 'Option 1'}, {'name': 'Option 2'}]' (optional)
    :param str font: Font to use for button text. Allows [Roboto, Roboto-Mono] Defaults to 'Roboto' (optional)
    :param str materialSides: Which sides display the rendered UI material Allows [both, front] Defaults to 'both' (optional)
    :param str theme: Color Theme Allows [light, dark] Defaults to 'light' (optional)
    :param str title: Title to display above buttons (optional). (optional)
    :param bool vertical: Vertical button layout (optional)
    """
    object_type = "arenaui-button-panel"

    def __init__(self, **kwargs):
        super().__init__(object_type=ButtonPanel.object_type, **kwargs)

    def json_preprocess(self, **kwargs):
        # kwargs are for additional param to add to json, like "action":"create"
        skipped_keys = [
            "evt_handler",
            "update_handler",
            "animations",
            "delayed_prop_tasks",
        ]
        json_payload = {k: v for k, v in vars(
            self).items() if k not in skipped_keys}
        json_payload["data"]["buttons"] = [
            vars(button) if hasattr(button, "__dict__") else button
            for button in json_payload["data"]["buttons"]
        ]
        json_payload.update(kwargs)
        return json_payload


class ButtonPanel(ArenauiButtonPanel):
    """
    Alternate name for ArenauiButtonPanel.
    """


class Button:
    """
    Buttons of a ButtonPanel in the ARENA UI.

    :param str name: Button Name
    :param str img: Image URl for image buttons (optional)
    :param float size: Size of image button (optional)
    :param float height: Height of image button, overrides size (optional)
    :param float: Width of image button, overrides size (optional)
    :param float borderRadius: Border radius of image button (optional)
    """

    def __init__(self, name="Button", **kwargs):
        self.name = name
        self.__dict__.update(kwargs)
