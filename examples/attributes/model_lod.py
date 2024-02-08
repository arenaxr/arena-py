from arena import *

scene = Scene(host="arenaxr.org", scene="example")


@scene.run_once
def make_lod_gltf():
    lod_gltf = GLTF(
        object_id="lod_gltf",
        url="store/models/Head2.glb",
        position=(0, 2, -3),
        gltf_model_lod=GltfModelLod(
            detailedUrl="store/models/BrainStem.glb",
            detailedDistance=6,
            updateRate=333,
            retainCache=False
        ),
    )
    scene.add_object(lod_gltf)


scene.run_tasks()
