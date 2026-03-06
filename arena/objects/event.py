from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

@dataclass
class Event:
    """
    Event
    Generate an event message for an object.

    :param str target: The `object_id` of event destination..
    :param dict targetPosition: The event destination position in 3D..
    :param dict originPosition: The event origination position in 3D., optional. Defaults to {'x': 0, 'y': 1.6, 'z': 0}
    :param str source: DEPRECATED: data.source is deprecated for clientEvent, use data.target instead., optional.
    :param dict position: DEPRECATED: data.position is deprecated for clientEvent, use data.targetPosition instead., optional.
    :param dict clickPos: DEPRECATED: data.clickPos is deprecated for clientEvent, use data.originPosition instead., optional.
    """
    target: str
    targetPosition: dict
    originPosition: Optional[dict] = field(default_factory=lambda: {'x': 0, 'y': 1.6, 'z': 0})
    source: Optional[str] = None
    position: Optional[dict] = None
    clickPos: Optional[dict] = None
