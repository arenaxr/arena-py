from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

@dataclass
class ArenaSceneOptions:
    """
    Scene Config

    :param dict env-presets: A-Frame Environment presets. More properties at <a href='https://github.com/supermedium/aframe-environment-component'>A-Frame Environment Component</a>..
    :param dict renderer-settings: These settings are fed into three.js WebGLRenderer properties., optional.
    :param dict scene-options: ARENA Scene Options..
    :param dict post-processing: These effects are enabled in desktop and XR views., optional.
    """
    env-presets: dict
    renderer-settings: Optional[dict] = None
    scene-options: dict
    post-processing: Optional[dict] = None
