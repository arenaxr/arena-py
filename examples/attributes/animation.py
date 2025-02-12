"""Animate

Animate and tween values.

More properties at <a href='https://aframe.io/docs/1.5.0/components/animation.html'>A-Frame Animation</a> component. Easing properties are detailed at <a href='https://easings.net'>easings.net</a>.

Animate rotation of three torii.

Other animations are available that resemble the `"data": {"animation": { "property": ... }}` blob above: see [A-Frame Animation](https://aframe.io/docs/1.5.0/components/animation.html) documentation for more examples.
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")

my_torus1 = Torus(
    object_id="my_torus1",
    position=(0, 2, 0),
    radius=0.75,
    persist=True,
)

my_torus2 = Torus(
    object_id="my_torus2",
    position=(0, 4, 0),
    radius=0.5,
    persist=True,
)

my_torus3 = Torus(
    object_id="my_torus3",
    position=(0, 6, 0),
    radius=0.25,
    persist=True,
)


@scene.run_once
def move_torus1():
    my_torus1.dispatch_animation(
        Animation(
            property="position",
            start=Position(0, 2, 0),
            end=Position(-5, 2, -5),
            easing="linear",
            dur=8000,
        )
    )
    my_torus1.dispatch_animation(
        Animation(
            property="rotation",
            start=Rotation(0, 0, 0),
            end=Rotation(0, 360, 0),
            easing="linear",
            dur=2000,
            loop=True,
        )
    )
    scene.update_object(my_torus1)


@scene.run_once
def move_torus2():
    my_torus2.dispatch_animation(
        Animation(
            property="position",
            start=Position(0, 4, 0),
            end=Position(-5, 4, -5),
            easing="easeInQuad",
            dur=4000,
        )
    )
    scene.update_object(my_torus2)


@scene.run_once
def move_torus3():
    my_torus3.dispatch_animation(
        Animation(
            property="position",
            start=Position(0, 6, 0),
            end=Position(-5, 6, -5),
            easing="linear",
            dur=6000,
        )
    )
    scene.update_object(my_torus3)


def cancel_torus1_move():
    print("Cancelling animation and jumping torus1 to new location")
    scene.update_object(my_torus1, position=Position(-8, 2, -5))  # Move to new spot


def change_torus2_color():
    print("Changing torus2 color (should not affect animation")
    scene.update_object(my_torus2, material=Material(color=Color(255, 0, 0)))  # Change color to red


def change_torus3_animation():
    print(
        "Overriding torus3 animation and cancelling original task. Note that the "
        "position update will not be in correct position because we are not yet "
        "also performing interp on position changes in arena-py"
    )
    my_torus3.dispatch_animation(
        Animation(
            property="position",
            start=Position(-2.5, 6, -2.5),
            end=Position(0, 6, 0),
            easing="linear",
            dur=1500,
        )
    )
    scene.update_object(my_torus3)


scene.add_object(my_torus1)
scene.add_object(my_torus2)
scene.add_object(my_torus3)
scene.run_after_interval(cancel_torus1_move, 5000)
scene.run_after_interval(change_torus2_color, 2000)
scene.run_after_interval(change_torus3_animation, 3000)
print("Moving all shapes in same direction")
scene.run_tasks()
