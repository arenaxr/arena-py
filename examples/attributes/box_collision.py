from arena import *


scene = Scene(host="arenaxr.org", scene="example")


def box_event(scene, evt, msg):
    print(f"Event {evt.type} received on object {evt.object_id}!")
    if evt.type == "collision-start":
        # show green ball at point of collision start
        add_temp_ball(scene, evt["data"]["position"], "green")
    elif evt.type == "collision-end":
        # show red ball at point of collision end
        add_temp_ball(scene, evt["data"]["position"], "red")


def add_temp_ball(scene, position, color):
    scene.add_object(Sphere(
        ttl=1,
        position=position,
        scale=(0.05, 0.05, 0.05),
        material=Material(color=color)
    ))


@scene.run_once
def make_box_collision():
    box_collision = Box(
        object_id="cube1",
        depth=1,
        height=1,
        width=3,
        position=(-3, 1, -2),
        material=Material(color="#b8ea2e", transparent=True, opacity=0.3),
        box_collision_listener=BoxCollisionListener(
            dynamic=False,
            enabled=True,
        ),
        clickable=True,
        evt_handler=box_event,

    )
    scene.add_object(box_collision)


scene.run_tasks()
