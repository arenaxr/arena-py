from .arena_object import Object

class Text(Object):
    """
    Class for Text in the ARENA: Display text.  More properties at (https://aframe.io/docs/1.5.0/components/text.html) A-Frame Text.
    
    :param str align: Multi-line text alignment. [left, center, right], defaults to 'left' (optional)
    :param float alphaTest: Discard text pixels if alpha is less than this value., defaults to '0.5' (optional)
    :param str anchor: Horizontal positioning. [left, right, center, align], defaults to 'center' (optional)
    :param str baseline: Vertical positioning. [top, center, bottom], defaults to 'center' (optional)
    :param str color: Text color., defaults to '#000000' (optional)
    :param str font: Font to render text, either the name of one of A-Frame's stock fonts or a URL to a font file [aileronsemibold, dejavu, exo2bold, exo2semibold, kelsonsans, monoid, mozillavr, roboto, sourcecodepro], defaults to 'roboto' (optional)
    :param str fontImage: Font image texture path to render text. Defaults to the font's name with extension replaced to .png. Don't need to specify if using a stock font. (derived from font name) (optional)
    :param float height: Height of text block. (derived from text size) (optional)
    :param float letterSpacing: Letter spacing in pixels. (optional)
    :param float lineHeight: Line height in pixels. (derived from font file) (optional)
    :param float opacity: Opacity, on a scale from 0 to 1, where 0 means fully transparent and 1 means fully opaque., defaults to '1' (optional)
    :param str shader: Shader used to render text. [portal, flat, standard, sdf, msdf, ios10hls, skyshader, gradientshader], defaults to 'sdf' (optional)
    :param str side: Side to render. [front, back, double], defaults to 'double' (optional)
    :param float tabSize: Tab size in spaces., defaults to '4' (optional)
    :param bool transparent: Whether text is transparent., defaults to 'True' (optional)
    :param str value: The actual content of the text. Line breaks and tabs are supported with \n and \t. (optional)
    :param str whiteSpace: How whitespace should be handled. [normal, pre, nowrap], defaults to 'normal' (optional)
    :param float width: Width in meters. (derived from geometry if exists), defaults to '5' (optional)
    :param float wrapCount: Number of characters before wrapping text (more or less)., defaults to '40' (optional)
    :param float wrapPixels: Number of pixels before wrapping text. (derived from wrapCount) (optional)
    :param float xOffset: X-offset to apply to add padding. (optional)
    :param float zOffset: Z-offset to apply to avoid Z-fighting if using with a geometry as a background., defaults to '0.001' (optional)
    """
    object_type = "text"

    def __init__(self, text="placeholder text", **kwargs):
        super().__init__(object_type=Text.object_type, text=text, **kwargs)
