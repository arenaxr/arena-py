"""360 Video Material

Draw a sphere geometry, set the texture src to be an equirectangular video on the inside of the sphere to create an immersive 360 video environment.

URLs work in the URL parameter slot. For example, `store/users/wiselab/images/360falls.mp4` or a full URL like `https://arenaxr.org/videos/360.mp4`.
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")


@scene.run_once
def make_video360():
    my_sphere = Sphere(
        object_id="sphere_vid",
        scale=(200, 200, 200),
        rotation=(0, 0.7, 0, 0.7),
        material=Material(
            src="store/users/wiselab/images/360falls.mp4",
            side="back",
        ),
    )
    scene.add_object(my_sphere)


scene.run_tasks()
