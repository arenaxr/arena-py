import json
from .arena_object import Object
from ..attributes import Morph

class GLTF(Object):
    """
    Class for GLTF Model in the ARENA.
    """
    def __init__(self, url="", **kwargs):
        self.morphs = []
        super().__init__(object_type="gltf-model", url=url, **kwargs)

    def update_morph(self, morph):
        if isinstance(morph, (list,tuple)):
            self.morphs += list(morph)
        elif isinstance(morph, Morph):
            self.morphs += [morph]
        return self.morphs

    def remove_morph_at_index(self, idx):
        if 0 <= idx < len(self.morphs):
            return self.morphs.pop(idx)
        return -1

    def clear_morphs(self):
        self.morphs = []

    def json_preprocess(self, **kwargs):
        # kwargs are for additional param to add to json, like "action":"create"
        json_payload = { k:v for k,v in vars(self).items() if not callable(v) and k != "animations" and k != "morphs" }
        json_payload.update(kwargs)
        return json_payload

    def json_postprocess(self, json_payload, json_data):
        for i,morph in enumerate(self.morphs):
            json_data[f"gltf-morph__{i}"] = vars(morph)
