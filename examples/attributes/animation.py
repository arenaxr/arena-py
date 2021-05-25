from arena import *

scene = Scene(host="arenaxr.org", scene="example")

my_torus = Torus(
    object_id="my_torus",
    position=(0,2,-5),
    scale=(1.0,1.0,1.0),
)

@scene.run_once
def rotate_torus():
    my_torus.dispatch_animation(
            Animation(property="rotation",start=(0,0,0),end=(0,360,0),easing="linear",dur=1000)
        )
    scene.update_object(my_torus)

scene.run_tasks()
