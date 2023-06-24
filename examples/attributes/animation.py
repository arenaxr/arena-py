from arena import *

scene = Scene(host="arenaxr.org", scene="example", debug=True)

my_torus1 = Torus(
    object_id="my_torus1",
    position=(0, 2, 0),
    radius=1,
    persist=True,
)

my_torus2 = Torus(
    object_id="my_torus2",
    position=(0, 4, 0),
    radius=0.5,
    persist=True,
)


@scene.run_once
def move_torus1():
    my_torus1.dispatch_animation(
        Animation(property="Position", start=(0, 2, 0), end=(-5, 2, -5),
                  easing="linear", dur=8000)
    )
    my_torus1.dispatch_animation(
        Animation(property="Rotation", start=(0, 0, 0), end=(0, 360, 0),
                  easing="linear", dur=2000, loop=True)
    )
    scene.update_object(my_torus1)


@scene.run_once
def move_torus2():
    my_torus2.dispatch_animation(
        Animation(property="Position", start=(0, 4, 0), end=(-5, 4, -5),
                  easing="easeInQuad", dur=4000)
    )
    scene.update_object(my_torus2)


def cancel_torus1_move():
    scene.update_object(my_torus1, Position=(-6, 2, -6))  # Move to new spot


scene.add_object(my_torus1)
scene.add_object(my_torus2)
scene.run_after_interval(cancel_torus1_move, 5000)
scene.run_tasks()
