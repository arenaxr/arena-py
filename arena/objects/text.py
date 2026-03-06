from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

@dataclass
class Text:
    """
    Text
    Display text. More properties at <a href='https://aframe.io/docs/1.5.0/components/text.html'>A-Frame Text</a>.

    :param str object_type: 3D object type.. Must be 'text'.
    :param str align: Multi-line text alignment., optional. Allows ['left', 'center', 'right']. Defaults to 'left'
    :param float alphaTest: Discard text pixels if alpha is less than this value., optional. Defaults to 0.5
    :param str anchor: Horizontal positioning., optional. Allows ['left', 'right', 'center', 'align']. Defaults to 'center'
    :param str baseline: Vertical positioning., optional. Allows ['top', 'center', 'bottom']. Defaults to 'center'
    :param str color: Text color.. Defaults to '#000000'
    :param str font: Font to render text, either the name of one of A-Frame's stock fonts or a URL to a font file.. Allows ['aileronsemibold', 'dejavu', 'exo2bold', 'exo2semibold', 'kelsonsans', 'monoid', 'mozillavr', 'roboto', 'sourcecodepro']. Defaults to 'roboto'
    :param float letterSpacing: Letter spacing in pixels., optional. Defaults to 0
    :param float opacity: Opacity, on a scale from 0 to 1, where 0 means fully transparent and 1 means fully opaque., optional. Defaults to 1
    :param str shader: Shader used to render text., optional. Allows ['portal', 'flat', 'standard', 'sdf', 'msdf', 'ios10hls', 'skyshader', 'gradientshader']. Defaults to 'sdf'
    :param str side: Side to render.. Allows ['front', 'back', 'double']. Defaults to 'double'
    :param float tabSize: Tab size in spaces., optional. Defaults to 4
    :param str text: DEPRECATED: data.text is deprecated for object_type: text, use data.value instead., optional.
    :param bool transparent: Whether text is transparent., optional. Defaults to True
    :param str value: The actual content of the text. Line breaks and tabs are supported with `\n` and `\t`..
    :param str whiteSpace: How whitespace should be handled., optional. Allows ['normal', 'pre', 'nowrap']. Defaults to 'normal'
    :param float wrapCount: Number of characters before wrapping text (more or less)., optional. Defaults to 40
    :param float xOffset: X-offset to apply to add padding., optional. Defaults to 0
    :param float zOffset: Z-offset to apply to avoid Z-fighting if using with a geometry as a background., optional. Defaults to 0.001
    """
    object_type: str
    align: Optional[str] = 'left'
    alphaTest: Optional[float] = 0.5
    anchor: Optional[str] = 'center'
    baseline: Optional[str] = 'center'
    color: str = '#000000'
    font: str = 'roboto'
    letterSpacing: Optional[float] = 0
    opacity: Optional[float] = 1
    shader: Optional[str] = 'sdf'
    side: str = 'double'
    tabSize: Optional[float] = 4
    text: Optional[str] = None
    transparent: Optional[bool] = True
    value: str
    whiteSpace: Optional[str] = 'normal'
    wrapCount: Optional[float] = 40
    xOffset: Optional[float] = 0
    zOffset: Optional[float] = 0.001
