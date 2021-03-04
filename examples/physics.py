from arena import *
import pybullet as p
import time
import pybullet_data
import asyncio

UPDATE_INTERVAL = 1 / 60
PHYSICS_INTERVAL = 1 / 1000
SYNC_INTERVAL = 1 / 100
physicsClient = p.connect(p.DIRECT)
p.setGravity(0, 0, -9.8 / 3)
user_cams = {}

def swap_yz(pos, round_decimals=None):
    """
    Swaps y and z axis, where AFrame uses y as vertical, pybullet uses z.
    :param pos: Array-like of len 3
    :param round_decimals: int, defaults to None (no rounding), optional
    :return: list
    """
    if round_decimals is not None:
        return [round(pos[0], round_decimals), round(pos[2], round_decimals),
                round(pos[1], round_decimals)]
    else:
        return [pos[0], pos[2], pos[1]]


def swap_rot(pos):
    return [-pos[0], -pos[2], -pos[1], pos[3]]


def new_user_handler(_scene, obj, _payload):
    d = obj.data
    new_sphere = p.loadURDF("sphere2.urdf", [d.position.x, d.position.z, d.position.y])
    p.changeDynamics(new_sphere, -1, restitution=2, mass=0, lateralFriction=1,
                     localInertiaDiagonal=(0, 0, 0))
    user_cams[obj.object_id] = {"bullet_id": new_sphere, "timestamp": time.time()}


def left_user_handler(_scene, obj, _payload):
    if user_cams.get(obj.object_id):
        user_cams.pop(obj.object_id)


def reset_ball(_scene, evt, _msg):
    if evt.type == "mousedown":
        print("Reset")
        p.resetBasePositionAndOrientation(ball, start_pos, start_orientation)
        if ball2:
            p.resetBasePositionAndOrientation(ball2, start_pos2, start_orientation)


scene = Scene(host="arena-dev1.conix.io", realm="realm", namespace="public",
              scene="physics", user_join_callback=new_user_handler,
              user_left_callback=left_user_handler, network_loop_interval=16)

arena_ball, arena_ball2 = None, None

start_pos = [0, 0.2, 15]
start_pos2 = [0.2, 0, 5]
start_orientation = p.getQuaternionFromEuler([0, 0, 0])
p.setAdditionalSearchPath(pybullet_data.getDataPath())

plane_id = p.loadURDF("plane.urdf", 0, 0, 0.3)
p.changeDynamics(plane_id, -1, restitution=0.99)

ball = p.loadURDF("soccerball.urdf", start_pos, start_orientation, globalScaling=1.5)
p.changeDynamics(ball, -1, restitution=0.99)

ball2 = p.loadURDF("soccerball.urdf", start_pos2, start_orientation, globalScaling=1.5)
p.changeDynamics(ball2, -1, restitution=0.99)


@scene.run_once
def init_scene():
    global arena_ball, arena_ball2

    arena_ball = GLTF(
        url="https://xr.andrew.cmu.edu/models/soccerball.gltf",
        position=swap_yz(start_pos), scale=(1.5, 1.5, 1.5), object_id="ball1",
        clickable=True, evt_handler=reset_ball, persist=True,
        # dynamic_body={"type":"dynamic", "mass":1, "shape":"sphere", "linearDamping":0.03,
        #              "angularDamping":0.03, "sphereRadius": 1.5}
    )

    grass = Box(
        position=[0, 0.15, 0], scale=[120, 0.3, 80], object_id="grass", persist=True,
        material=Material(color=(49, 114, 41)),
        # dynamic_body={"type":"static", "mass":0}
        # dynamic_body=Physics(type="dynamic"))
    )
    # arena_ball = Sphere(position=swap_yz(start_pos), scale=(1, 1, 1), object_id="ball1")

    arena_ball2 = GLTF(
        url="https://xr.andrew.cmu.edu/models/soccerball.gltf",
        position=swap_yz(start_pos2), scale=(1.5, 1.5, 1.5), object_id="ball2",
        clickable=True, evt_handler=reset_ball, persist=True,
        # dynamic_body={"type":"dynamic", "mass":1, "shape":"sphere", "linearDamping":0.03,
        #              "angularDamping":0.03, "sphereRadius": 1.5}
    )

    # arena_ball2 = Sphere(position=swap_yz(start_pos2), rotation=start_orientation,
    #                     scale=(0.5, 0.5, 0.5), object_id="ball2")

    scene.add_object(arena_ball)
    scene.add_object(grass)
    scene.add_object(arena_ball2)


@scene.run_async
async def sync_world():
    while True:
        for c in user_cams.items():
            scene_user = scene.users.get(c[0])
            if scene_user:
                new_pos = [scene_user.data.position.x, scene_user.data.position.z,
                           scene_user.data.position.y]
                update_sphere_id = c[1]["bullet_id"]
                prev_pos, _ = p.getBasePositionAndOrientation(update_sphere_id)
                if new_pos != list(prev_pos):
                    p.resetBasePositionAndOrientation(update_sphere_id, new_pos,
                                                      start_orientation)
        await asyncio.sleep(SYNC_INTERVAL)


@scene.run_async
async def step_ball_async():
    j = 0
    colliding = False
    push_update = False
    ball_pos, ball_rot = None, None
    velocity = None
    while True:
        if push_update:
            lin_v, ang_v = p.getBaseVelocity(ball)
            ball_pos, ball_rot = p.getBasePositionAndOrientation(ball)
            velocity = {
                "linear": swap_yz(lin_v, round_decimals=3),
                "angular": swap_yz(ang_v, round_decimals=3),
            }
        p.stepSimulation()
        collisions = p.getContactPoints(ball)
        if len(collisions):
            pass
            colliding = True
        else:
            # push_update = colliding
            colliding = False
        if j % (UPDATE_INTERVAL // PHYSICS_INTERVAL) == 0:
            if push_update and velocity is not None:
                print("velocity update", velocity)
                scene.update_object(arena_ball, position=swap_yz(ball_pos),
                                    rotation=swap_rot(ball_rot), velocity=velocity)
                push_update = False
                velocity = False
            else:
                pass
                ball_pos, ball_rot = p.getBasePositionAndOrientation(ball)
                scene.update_object(arena_ball, position=swap_yz(ball_pos),
                                    rotation=swap_rot(ball_rot))
                ball_pos2, ball_rot2 = p.getBasePositionAndOrientation(ball2)
                scene.update_object(arena_ball2, position=swap_yz(ball_pos2),
                                    rotation=swap_rot(ball_rot2))
        j += 1
        await asyncio.sleep(PHYSICS_INTERVAL)


scene.run_tasks()
