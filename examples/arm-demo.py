# arm-demo.py
#
# Install a robot arm and two buttons that start and stop an animation
from arena import *


def end_program_callback(scene: Scene):
    global sceneParent
    scene.delete_object(sceneParent)


# command line options
arena = Scene(cli_args=True, end_program_callback=end_program_callback)
app_position = arena.args["position"]
app_rotation = arena.args["rotation"]
app_scale = arena.args["scale"]

# variables
arm_scale = 0.01
button_scale = (0.5, 0.1, 0.5)


def draw_ray(clickPos, position):
    line = ThickLine(
        ttl=1,
        lineWidth=5,
        # slightly below camera so you can see line vs head-on
        path=((clickPos.x, clickPos.y-0.2, clickPos.z),
              (position.x, position.y, position.z)),
        color="#FF00FF",
    )
    arena.add_object(line)


def start_handler(scene, evt, msg):
    global arm_model
    if evt.type == "mousedown":
        draw_ray(evt.data.clickPos, evt.data.position)
        arm_model.dispatch_animation(
            AnimationMixer(clip="Armature.002|Armature.002Action.001")
        )
        scene.run_animations(arm_model)


def stop_handler(scene, evt, msg):
    global arm_model
    if evt.type == "mousedown":
        draw_ray(evt.data.clickPos, evt.data.position)
        arm_model.dispatch_animation(
            AnimationMixer(clip="pause")
        )
        scene.run_animations(arm_model)


def arm_click_handler(scene, evt, msg):
    if evt.type == "mousedown":
        draw_ray(evt.data.clickPos, evt.data.position)


@arena.run_once
def main():
    global arm_model, sceneParent
    # make a parent scene object
    sceneParent = Object(
        persist=True,
        object_id="arm-sceneParent",
        position=app_position,
        rotation=app_rotation,
        scale=app_scale,
    )
    arena.add_object(sceneParent)

    arm_model = GLTF(
        object_id="arm_model",
        url="/store/models/factory_robot_arm/scene.gltf",
        position=(0, 0, 0),
        scale=(arm_scale, arm_scale, arm_scale),
        clickable=True,
        parent=sceneParent.object_id,
        persist=True,
        evt_handler=arm_click_handler,
    )
    arena.add_object(arm_model)
    arm_start_button = Box(
        object_id="arm_start_button",
        position=(0.5, 0, 2),
        scale=button_scale,
        clickable=True,
        color=(0, 255, 0),
        parent=sceneParent.object_id,
        persist=True,
        evt_handler=start_handler,
    )
    arena.add_object(arm_start_button)
    arm_stop_button = Box(
        object_id="arm_stop_button",
        position=(-0.5, 0, 2),
        scale=button_scale,
        clickable=True,
        color=(255, 0, 0),
        parent=sceneParent.object_id,
        persist=True,
        evt_handler=stop_handler,
    )
    arena.add_object(arm_stop_button)
    arm_start_txt = Text(
        object_id="arm_start_txt",
        position=(0, 0.75, 1.5),
        parent=sceneParent.object_id,
        text="Red and green buttons will run some interactive networked Python code.",
        color="#555555",
        persist=True,
    )
    arena.add_object(arm_start_txt)

    # source
    arm_src_img = Plane(
        object_id="arm_src_img",
        position=(3, 1, -2),
        scale=(1.75, 0.5, 1),
        parent=sceneParent.object_id,
        color="#ffffff",
        clickable=True,
        goto_url=GotoUrl(dest="newtab", on="mousedown",
                         url="https://github.com/conix-center/ARENA-py/blob/master/examples/arm-demo.py"),
        persist=True,
    )
    arena.add_object(arm_src_img)
    arm_src_txt = Text(
        object_id="arm_src_txt",
        position=(3, 1, -2),
        parent=sceneParent.object_id,
        text="Click for source",
        color="#555555",
        persist=True,
    )
    arena.add_object(arm_src_txt)


arena.run_tasks()
