import json
from .arena_object import Object
from ..attributes import Morph

class GLTF(Object):
    """
    Class for GLTF Models in the ARENA.
    """
    object_type = "gltf-model"

    def __init__(self, url="", **kwargs):
        self.morphs = {}
        super().__init__(object_type=GLTF.object_type, url=url, **kwargs)

    def update_morph(self, morph):
        if isinstance(morph, (list,tuple)):
            for m in morph:
                self.morphs[m.morphtarget] = m
        elif isinstance(morph, Morph):
            self.morphs[morph.morphtarget] = morph
        return self.morphs

    def remove_morph(self, morph):
        if morph.morphtarget in self.morphs:
            del self.morphs[morph.morphtarget]

    def clear_morphs(self):
        self.morphs = {}

    def json_preprocess(self, **kwargs):
        # kwargs are for additional param to add to json, like "action":"create"
        json_payload = { k:v for k,v in vars(self).items() if not callable(v) and k != "animations" and k != "morphs" }
        json_payload.update(kwargs)
        return json_payload

    def json_postprocess(self, json_payload, json_data):
        for i,morph in enumerate(self.morphs.values()):
            json_data[f"gltf-morph__{i}"] = vars(morph)

class Model(GLTF):
    """
    Another name for GLTF.
    """
