from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

@dataclass
class ArenauiButtonPanel:
    """
    ARENAUI Button Panel
    ARENAUI element which displays a vertical or horizontal panel of buttons.

    :param str object_type: 3D object type.. Must be 'arenaui-button-panel'.
    :param list buttons: Buttons. Defaults to [{'name': 'Option 1'}, {'name': 'Option 2'}]
    :param str title: Title to display above buttons (optional).. Defaults to ''
    :param bool vertical: Vertical button layout. Defaults to False
    :param str font: Font to use for button text., optional. Allows ['Roboto', 'Roboto-Mono']. Defaults to 'Roboto'
    :param str theme: Color Theme, optional. Allows ['light', 'dark']. Defaults to 'light'
    :param str materialSides: Which sides display the rendered UI material, optional. Allows ['both', 'front']. Defaults to 'both'
    """
    object_type: str
    buttons: list = field(default_factory=lambda: [{'name': 'Option 1'}, {'name': 'Option 2'}])
    title: str = ''
    vertical: bool = False
    font: Optional[str] = 'Roboto'
    theme: Optional[str] = 'light'
    materialSides: Optional[str] = 'both'
