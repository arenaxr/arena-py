import re
import webcolors
from ..utils import *
from .attribute import Attribute
from .position import Position
from .rotation import Rotation
from .scale import Scale
from .color import Color

class Data(Attribute):
    """
    Data Attribute. Wraps all attributes in JSON.
    """
    def __init__(self, **kwargs):
        data = {}
        data = Data.update_data(data, kwargs)
        super().__init__(**data)

    @classmethod
    def update_data(cls, data, new_data):
        new_data = new_data.get("data", new_data)
        dash_words = []
        for k,v in new_data.items():
            # the dashes in these specific keys need to be replaced with underscores
            if k == "goto-url":
                dash_words += [k]
                k = "goto_url"
                if isinstance(v, dict):
                    data[k] = GotoUrl(**v)
                else:
                    data[k] = v

            # this could be called "clickable"
            if k == "click-listener":
                if "clickable" in data:
                    k = "clickable"
                else:
                    dash_words += [k]
                    k = "click_listener"
                data[k] = v

            # this could be called "physics"
            if k == "dynamic-body":
                if "physics" in data:
                    k = "physics"
                else:
                    dash_words += [k]
                    k = "dynamic_body"
                if isinstance(v, dict):
                    data[k] = Physics(**v)
                else:
                    data[k] = v

            # allow user to input tuples, lists, dicts, etc for specific Attributes.
            # everything gets converted to corresponding attribute
            if k == "position" and not isinstance(v, Position):
                if isinstance(v, tuple) or isinstance(v, list):
                    data[k] = Position(*v[:3])
                elif isinstance(v, dict):
                    data[k] = Position(**v)
                else:
                    data[k] = v

            elif k == "rotation" and not isinstance(v, Rotation):
                if isinstance(v, tuple) or isinstance(v, list):
                    if len(v) == 3:
                        data[k] = Rotation(*v[:3], None)
                    else:
                        data[k] = Rotation(*v[:4])
                elif isinstance(v, dict):
                    # rotation doesnt exist or rotation originally in euler
                    if k not in data or not data[k].is_quaternion:
                        v = Rotation.q2e((v["x"], v["y"], v["z"], v["w"]))
                        data[k] = Rotation(*v)
                    else:
                        data[k] = Rotation(**v)
                else:
                    data[k] = v

            elif k == "scale" and not isinstance(v, Scale):
                if isinstance(v, tuple) or isinstance(v, list):
                    data[k] = Scale(*v[:3])
                elif isinstance(v, dict):
                    data[k] = Scale(**v)
                else:
                    data[k] = v

            elif k == "color":
                if isinstance(v, tuple) or isinstance(v, list):
                    data[k] = Color(*v[:3])
                elif isinstance(v, dict):
                    data[k] = Color(**v)
                elif isinstance(v, str):
                    # hex to tuple to Color
                    color = v.lstrip('#')
                    hexcolor = re.search(r'^(?:[0-9a-fA-F]{3}){1,2}$', color)
                    if not hexcolor:
                        try:
                            wcrgb = webcolors.name_to_rgb(color)
                        except:
                            wcrgb = webcolors.hex_to_rgb("#0"+color)
                        v = (wcrgb.red, wcrgb.green, wcrgb.blue)
                    else:
                        v = tuple(int(color[c:c+2], 16) for c in (0, 2, 4))
                    data[k] = Color(*v)
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

            # make False into None
            if (isinstance(v, bool) and v == False) or v is None:
                data[k] = None

        # delete elements with keys that have dashes
        for w in dash_words:
            if w in data:
                del data[w]

        return data
