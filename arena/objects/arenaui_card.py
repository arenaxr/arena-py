from .arena_object import Object

class ArenauiCard(Object):
    """
    ArenauiCard object class to manage its properties in the ARENA: ARENAUI element which displays text and optionally an image.
    
    :param str title: Title (optional)
    :param str body: This is the text body of the card. (optional)
    :param str bodyAlign: Body Text Alignment [left, center, right, justify]; defaults to 'left' (optional)
    :param str img: This image will be embedded alongside the body text (optional)
    :param str imgCaption: This will caption the image (optional)
    :param str imgDirection: Image Direction [left, right]; defaults to 'right' (optional)
    :param str imgSize: Image sizing [cover, contain, stretch]; defaults to 'cover' (optional)
    :param float textImageRatio: Text to Image Width Ratio; defaults to '0.5' (optional)
    :param float fontSize: Font Size; defaults to '0.035' (optional)
    :param float widthScale: Width scale multiplier; defaults to '1' (optional)
    :param bool closeButton: Show close button (optional)
    :param str font: Font to use for button text [Roboto, Roboto-Mono]; defaults to 'Roboto' (optional)
    :param str theme: Color Theme [light, dark]; defaults to 'light' (optional)
    """
    object_type = "arenaui-card"

    def __init__(self, **kwargs):
        super().__init__(object_type=ArenauiCard.object_type, **kwargs)


class Card(ArenauiCard):
    """
    Alternate name for ArenauiCard.
    """
