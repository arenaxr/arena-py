# arm-demo.py
#
# Install a robot arm and two buttons that start and stop an animation
from arena import *


def end_program_callback(scene: Scene):
    global arm_model
    scene.delete_object(arm_model)


# command line options
arena = Scene(cli_args=True, end_program_callback=end_program_callback)
app_position = arena.args["position"]
app_rotation = arena.args["rotation"]

# variables
arm_scale = 0.01
start_position_child = ((app_position[0]+0.5)/arm_scale,
                        (app_position[1])/arm_scale,
                        (app_position[2]+6)/arm_scale)
stop_position_child = ((app_position[0]-0.5)/arm_scale,
                       (app_position[1])/arm_scale,
                       (app_position[2]+6)/arm_scale)
text_position_child = ((app_position[0])/arm_scale,
                       (app_position[1]+0.25)/arm_scale,
                       (app_position[2]+5.25)/arm_scale)
button_scale_child = (0.5/arm_scale, 0.1/arm_scale, 0.5/arm_scale)
text_scale_child = (1/arm_scale, 1/arm_scale, 1/arm_scale)
text_rotation_child = (app_rotation[0], app_rotation[1], app_rotation[2])


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
    global arm_model
    arm_model = GLTF(
        object_id="arm_model",
        url="/store/models/factory_robot_arm/scene.gltf",
        rotation=app_rotation,
        position=app_position,
        scale=(arm_scale, arm_scale, arm_scale),
        clickable=True,
        persist=True,
        evt_handler=arm_click_handler
    )
    arena.add_object(arm_model)
    arm_start_button = Box(
        object_id="arm_start_button",
        position=start_position_child,
        scale=button_scale_child,
        clickable=True,
        color=(0, 255, 0),
        parent=arm_model.object_id,
        persist=True,
        evt_handler=start_handler
    )
    arena.add_object(arm_start_button)
    arm_stop_button = Box(
        object_id="arm_stop_button",
        position=stop_position_child,
        scale=button_scale_child,
        clickable=True,
        color=(255, 0, 0),
        parent=arm_model.object_id,
        persist=True,
        evt_handler=stop_handler
    )
    arena.add_object(arm_stop_button)
    arm_start_txt = Text(
        object_id="arm_start_txt",
        # rotation=text_rotation_child,
        position=text_position_child,
        scale=text_scale_child,
        parent=arm_model.object_id,
        text="Red and green buttons will run some interactive networked Python code.",
        persist=True
    )
    arena.add_object(arm_start_txt)


arena.run_tasks()
