"""Look At

The look-at component defines the behavior for an entity to dynamically rotate or face towards another entity or position. Use `#my-camera` to face the user camera, otherwise can take either a vec3 position or a query selector to another entity.
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")


@scene.run_once
def make_rotating_image():
    rotating_image = Image(
        object_id="rotating_image",
        url="store/users/wiselab/images/conix-face-white.jpg",
        position=Position(1, 2, -2),
        look_at="#my-camera",
    )
    scene.add_object(rotating_image)


scene.run_tasks()
