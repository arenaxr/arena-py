import json
from .arena_object import Object
from ..attributes import Morph

class GltfModel(Object):
    """
    GltfModel object class to manage its properties in the ARENA: Load a GLTF model.  Besides applying standard rotation and position attributes to the center-point of the GLTF model, the individual child components can also be manually manipulated. See format details in the `modelUpdate` data attribute. See guidance to store paths under <https://docs.arenaxr.org/content/interface/filestore.html> ARENA File Store, CDN, or DropBox.

    :param str url: Use File Store paths under 'store/users/username', see CDN and other storage options in the description above. (optional)
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
        skipped_keys = ["evt_handler", "update_handler", "delayed_prop_tasks",
                        "animations", "morphs"]
        json_payload = {k: v for k, v in vars(self).items() if
                        not callable(v) and k not in skipped_keys}
        json_payload.update(kwargs)
        return json_payload

    def json_postprocess(self, json_payload, json_data):
        for i,morph in enumerate(self.morphs.values()):
            json_data[f"gltf-morph__{i}"] = vars(morph)


class GLTF(GltfModel):
    """
    Another name for GltfModel.
    """


class Model(GltfModel):
    """
    Another name for GltfModel.
    """
