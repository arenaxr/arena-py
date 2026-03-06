from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

@dataclass
class ArenauiCard:
    """
    ARENAUI Card Panel
    ARENAUI element which displays text and optionally an image.

    :param str object_type: 3D object type.. Must be 'arenaui-card'.
    :param str title: Title. Defaults to ''
    :param str body: This is the text body of the card.. Defaults to ''
    :param str bodyAlign: Body Text Alignment, optional. Allows ['left', 'center', 'right', 'justify']. Defaults to 'left'
    :param str img: This image will be embedded alongside the body text., optional. Defaults to ''
    :param str imgCaption: This will caption the image., optional. Defaults to ''
    :param str imgDirection: Image Direction, optional. Allows ['left', 'right']. Defaults to 'right'
    :param str imgSize: Image sizing, optional. Allows ['cover', 'contain', 'stretch']. Defaults to 'cover'
    :param float textImageRatio: Text to Image Width Ratio, optional. Defaults to 0.5
    :param float fontSize: Font Size, optional. Defaults to 0.035
    :param float widthScale: Width scale multiplier, optional. Defaults to 1
    :param bool closeButton: Show close button, optional. Defaults to False
    :param str font: Font to use for button text., optional. Allows ['Roboto', 'Roboto-Mono']. Defaults to 'Roboto'
    :param str theme: Color Theme, optional. Allows ['light', 'dark']. Defaults to 'light'
    :param str materialSides: Which sides display the rendered UI material, optional. Allows ['both', 'front']. Defaults to 'both'
    """
    object_type: str
    title: str = ''
    body: str = ''
    bodyAlign: Optional[str] = 'left'
    img: Optional[str] = ''
    imgCaption: Optional[str] = ''
    imgDirection: Optional[str] = 'right'
    imgSize: Optional[str] = 'cover'
    textImageRatio: Optional[float] = 0.5
    fontSize: Optional[float] = 0.035
    widthScale: Optional[float] = 1
    closeButton: Optional[bool] = False
    font: Optional[str] = 'Roboto'
    theme: Optional[str] = 'light'
    materialSides: Optional[str] = 'both'
