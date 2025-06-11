# from deprecated import deprecated

from ..utils import *
from .attribute import Attribute
from .position import Position


class DataEvent(Attribute):
    def __init__(self, **kwargs):
        data = {}
        data = DataEvent.update_data(data, kwargs)
        super().__init__(**data)

    @classmethod
    def update_data(cls, data, new_data):
        new_data = new_data.get("data", new_data)
        for k, v in new_data.items():
            # allow user to input tuples, lists, dicts, etc for specific Attributes.
            # everything gets converted to corresponding attribute
            if (k == "originPosition" or k == "targetPosition") and not isinstance(v, Position):
                if isinstance(v, (list, tuple)):
                    data[k] = Position(*v[:3])
                elif isinstance(v, dict):
                    data[k] = Position(**v)
                else:
                    data[k] = v

            elif isinstance(v, Attribute):
                data[k] = v

            else:
                try:
                    # unknown attribute
                    data[k] = Attribute(**v)
                except:
                    data[k] = v

        return data

    @property
    # @deprecated("DEPRECATED: data.source is deprecated for clientEvent, use data.target instead.")
    def source(self):
        return None

    @source.setter
    # @deprecated("DEPRECATED: data.source is deprecated for clientEvent, use data.target instead.")
    def source(self, value):
        return

    @property
    # @deprecated("DEPRECATED: data.clickPos is deprecated for clientEvent, use data.originPosition instead.")
    def clickPos(self):
        return None

    @clickPos.setter
    # @deprecated("DEPRECATED: data.clickPos is deprecated for clientEvent, use data.originPosition instead.")
    def clickPos(self, value):
        return

    @property
    # @deprecated("DEPRECATED: data.position is deprecated for clientEvent, use data.targetPosition instead.")
    def position(self):
        return None

    @position.setter
    # @deprecated("DEPRECATED: data.position is deprecated for clientEvent, use data.targetPosition instead.")
    def position(self, value):
        return
