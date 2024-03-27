from .arena_object import Object


class Text(Object):
    """
    Text object class to manage its properties in the ARENA: Display text. More properties at <https://aframe.io/docs/1.5.0/components/text.html> A-Frame Text.

    :param str align: Multi-line text alignment. Allows [left, center, right] Defaults to 'left' (optional)
    :param float alphaTest: Discard text pixels if alpha is less than this value. Defaults to '0.5' (optional)
    :param str anchor: Horizontal positioning. Allows [left, right, center, align] Defaults to 'center' (optional)
    :param str baseline: Vertical positioning. Allows [top, center, bottom] Defaults to 'center' (optional)
    :param str color: Text color. Defaults to '#000000' (optional)
    :param str font: Font to render text, either the name of one of A-Frame's stock fonts or a URL to a font file. Allows [aileronsemibold, dejavu, exo2bold, exo2semibold, kelsonsans, monoid, mozillavr, roboto, sourcecodepro] Defaults to 'roboto' (optional)
    :param str fontImage: Font image texture path to render text. Defaults to the font's name with extension replaced to .png. Don't need to specify if using a stock font. (derived from font name). (optional)
    :param float height: Height of text block. (derived from text size). (optional)
    :param float letterSpacing: Letter spacing in pixels. (optional)
    :param float lineHeight: Line height in pixels. (derived from font file). (optional)
    :param float opacity: Opacity, on a scale from 0 to 1, where 0 means fully transparent and 1 means fully opaque. Defaults to '1' (optional)
    :param str shader: Shader used to render text. Allows [portal, flat, standard, sdf, msdf, ios10hls, skyshader, gradientshader] Defaults to 'sdf' (optional)
    :param str side: Side to render. Allows [front, back, double] Defaults to 'double' (optional)
    :param float tabSize: Tab size in spaces. Defaults to '4' (optional)
    :param bool transparent: Whether text is transparent. Defaults to 'True' (optional)
    :param str value: The actual content of the text. Line breaks and tabs are supported with `\\n` and `\\t`. (optional)
    :param str whiteSpace: How whitespace should be handled. Allows [normal, pre, nowrap] Defaults to 'normal' (optional)
    :param float width: Width in meters. (derived from geometry if exists). Defaults to '5' (optional)
    :param float wrapCount: Number of characters before wrapping text (more or less). Defaults to '40' (optional)
    :param float wrapPixels: Number of pixels before wrapping text. (derived from wrapCount). (optional)
    :param float xOffset: X-offset to apply to add padding. (optional)
    :param float zOffset: Z-offset to apply to avoid Z-fighting if using with a geometry as a background. Defaults to '0.001' (optional)
    """
    object_type = "text"

    def __init__(self, **kwargs):
        # NOTE: Don't require parameter 'text' or 'value' we won't know which one users
        #       used downstream into persist
        super().__init__(object_type=Text.object_type, **kwargs)
