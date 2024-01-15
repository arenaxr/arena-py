from .arena_object import Object


class ArenauiCard(Object):
    """
    Text/Image Card in the ARENA UI.

    :param str title: Title of Card (optional)
    :param str body: Body text of Card (optional)
    :param str bodyAlign: Text alignment of body text ['center', 'left', 'right', 'justify'] (optional)
    :param str img: Image URL of Card (optional)
    :param str imgCaption: Image caption (optional)
    :param str imgDirection: Left or Right image placement vs body text [ 'left', 'right'] (optional)
    :param str imgSize: Container size fitting of image ['cover', 'contain'] (optional)
    :param float fontSize: Font size of card, scales both title and body (optional)
    :param float widthScale: Width of card as a factor of the default (optional)
    :param bool closeButton: Whether to display a close button (optional)
    :param str font: Font of card ['Roboto', 'Roboto-Mono'] (optional)
    """
    object_type = "arenaui-card"

    def __init__(self, **kwargs):
        super().__init__(object_type=ArenauiCard.object_type, **kwargs)


class Card(ArenauiCard):
    """
    Alternate name for ArenauiCard.
    """
