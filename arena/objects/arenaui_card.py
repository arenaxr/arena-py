from .arena_object import Object

class ArenauiCard(Object):
    """
    ArenauiCard object class to manage its properties in the ARENA: ARENAUI element which displays text and optionally an image.

    :param str body: This is the text body of the card. (optional)
    :param str bodyAlign: Body Text Alignment Allows [left, center, right, justify] Defaults to 'left' (optional)
    :param bool closeButton: Show close button (optional)
    :param str font: Font to use for button text. Allows [Roboto, Roboto-Mono] Defaults to 'Roboto' (optional)
    :param float fontSize: Font Size Defaults to '0.035' (optional)
    :param str img: This image will be embedded alongside the body text. (optional)
    :param str imgCaption: This will caption the image. (optional)
    :param str imgDirection: Image Direction Allows [left, right] Defaults to 'right' (optional)
    :param str imgSize: Image sizing Allows [cover, contain, stretch] Defaults to 'cover' (optional)
    :param str materialSides: Which sides display the rendered UI material Allows [both, front] Defaults to 'both' (optional)
    :param float textImageRatio: Text to Image Width Ratio Defaults to '0.5' (optional)
    :param str theme: Color Theme Allows [light, dark] Defaults to 'light' (optional)
    :param str title: Title (optional)
    :param float widthScale: Width scale multiplier Defaults to '1' (optional)
    """
    object_type = "arenaui-card"

    def __init__(self, **kwargs):
        super().__init__(object_type=ArenauiCard.object_type, **kwargs)


class Card(ArenauiCard):
    """
    Alternate name for ArenauiCard.
    """
