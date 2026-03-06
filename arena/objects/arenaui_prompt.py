from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

@dataclass
class ArenauiPrompt:
    """
    ARENAUI Prompt
    ARENAUI element which displays prompt with button actions.

    :param str object_type: 3D object type.. Must be 'arenaui-prompt'.
    :param str title: Title. Defaults to 'Prompt'
    :param str description: Description, optional. Defaults to 'This is a prompt. Please confirm or cancel.'
    :param list buttons: Buttons. Defaults to ['Confirm', 'Cancel']
    :param float width: Override width. Defaults to 1.5
    :param str font: Font to use for button text., optional. Allows ['Roboto', 'Roboto-Mono']. Defaults to 'Roboto'
    :param str theme: Color Theme, optional. Allows ['light', 'dark']. Defaults to 'light'
    :param str materialSides: Which sides display the rendered UI material, optional. Allows ['both', 'front']. Defaults to 'both'
    """
    object_type: str
    title: str = 'Prompt'
    description: Optional[str] = 'This is a prompt. Please confirm or cancel.'
    buttons: list = field(default_factory=lambda: ['Confirm', 'Cancel'])
    width: float = 1.5
    font: Optional[str] = 'Roboto'
    theme: Optional[str] = 'light'
    materialSides: Optional[str] = 'both'
