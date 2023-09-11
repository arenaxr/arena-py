import random

from arena import *
import time
import asyncio
import pyphysx as physx
from pyphysx_utils.rate import Rate

# from pyphysx_render.pyrender_offscreen_renderer import PyPhysxOffscreenRenderer
from pyphysx_render.pyrender import PyPhysxViewer

from quaternion import quaternion, as_float_array

from typing import List

Vector = List[float]

BASE_ORIENTATION = quaternion(1, 0, 0, 0)


class debugDECODER(json.JSONEncoder):
    """
    Custom JSON encoder for nested BaseObjects.
    """

    def default(self, obj):
        if isinstance(obj, (tuple, list, dict)):
            return obj
        else:
            print("DECODING", obj)
            return vars(obj)


def swap_yz(pos: Vector, round_decimals: int = None):
    """
    Util to swap y and z axis, where AFrame uses y as vertical, pybullet uses z.
    :param pos: Array-like of len 3
    :param round_decimals: int, defaults to None (no rounding), optional
    :return: list
    """
    if round_decimals is not None:
        return [
            round(float(pos[0]), round_decimals),
            round(float(pos[2]), round_decimals),
            round(float(pos[1]), round_decimals),
        ]

    else:
        return [float(pos[0]), float(pos[2]), float(pos[1])]


def swap_rot(rot: Vector, round_decimals: int = None):
    """
    Util to swap y and z axis, where AFrame uses y as vertical, pybullet uses z.
    Also negates the rotation for yet unknown reason. Quaternion.as_float_array
    comes in as [w, x, y, z]
    :param rot: Array-like of len 4
    :param round_decimals: int, defaults to None (no rounding), optional
    :return: list
    """
    if round_decimals is not None:
        return [
            round(rot[1], round_decimals),
            round(rot[3], round_decimals),
            round(rot[2], round_decimals),
            round(rot[0], round_decimals),
        ]
    else:
        return [-rot[1], -rot[3], -rot[2], rot[0]]


class PhysicsSystem:
    """
    Physics system based on pybullet
    """

    def __init__(
        self,
        physics_rate=120,  # Default pybullet step = 1/240s
        physics_update_rate=60,  # Lower than engine rate
        physics_push_sync_rate=60,  # Frequency of mqtt object_updates pushes
        mqtt_sync_rate=60,  # Frequency of physics sync to mqtt object states
        gravity=-9.8,  # Gravity of physics system
        **kwargs,
    ):
        self.physics_rate = physics_rate
        self.physics_interval = 1 / physics_rate
        self.physics_update_rate = physics_update_rate
        self.physics_push_sync_rate = physics_push_sync_rate
        self.mqtt_sync_rate = mqtt_sync_rate

        self.physx_scene = physx.Scene()

        # p.setGravity(0, 0, gravity)
        # p.setTimeStep(self.physics_interval)

        self.scene = Scene(
            host="arena-dev1.conix.io",
            realm="realm",
            namespace="public",
            scene="physics",
            user_join_callback=self.new_user_handler,
            user_left_callback=self.left_user_handler,
            threaded=True,
        )
        self.user_cams = {}

        self.physx_scene.add_actor(
            physx.RigidStatic.create_plane(
                material=physx.Material(
                    static_friction=0.1, dynamic_friction=0.1, restitution=0.75
                )
            )
        )
        self.scene.add_object(
            Box(
                position=[0, 0.01, 0],
                scale=[120, 0.01, 80],
                object_id="grass",
                persist=True,
                material=Material(color=(49, 114, 41)),
            )
        )

        self.physx_rate = Rate(self.physics_rate * 2)

    def start(self):
        self.scene.run_async(self.sync_world)
        self.scene.run_tasks()

    def new_user_handler(self, _scene, obj, _payload):
        pass
        """
        Model users as 0.5m static spheres
        :param _scene:
        :param obj:
        :param _payload:
        :return:
        """
        # d = obj.data
        # new_sphere = p.loadURDF(
        #     "sphere2.urdf", [d.position.x, d.position.z, d.position.y]
        # )
        # p.changeDynamics(
        #     new_sphere,
        #     -1,
        #     restitution=0.75,
        #     mass=0,
        #     lateralFriction=1,
        #     localInertiaDiagonal=(0, 0, 0),
        # )
        # self.user_cams[obj.object_id] = {
        #     "phys_id": new_sphere,
        #     "timestamp": time.time(),
        # }

    def left_user_handler(self, _scene, obj, _payload):
        pass
        # if self.user_cams.get(obj.object_id):
        #     p.removeBody(self.user_cams.pop(obj.object_id)["phys_id"])

    async def sync_world(self):
        pass
        # while True:
        #     for c in self.user_cams.items():
        #         scene_user = self.scene.users.get(c[0])
        #         if scene_user:
        #             new_pos = [
        #                 scene_user.data.position.x,
        #                 scene_user.data.position.z,
        #                 scene_user.data.position.y,
        #             ]
        #             update_sphere_id = c[1]["phys_id"]
        #             prev_pos, _ = p.getBasePositionAndOrientation(update_sphere_id)
        #             if new_pos != list(prev_pos):
        #                 p.resetBasePositionAndOrientation(
        #                     update_sphere_id, new_pos, BASE_ORIENTATION
        #                 )
        #     await asyncio.sleep(1 / self.mqtt_sync_rate)


# TODO: Make generic phys-arena object class
class SoccerBall:
    def __init__(self, physx_scene, ball_id: int, start_pos: Vector = None):
        if start_pos is None:
            start_pos = [0, 0, 3]  # Start slightly above size of ball
        self.start_pos = start_pos
        self.prev_pos = swap_yz(start_pos, 3)
        self.start_orientation = BASE_ORIENTATION
        self.prev_rot = swap_rot(as_float_array(BASE_ORIENTATION), 3)
        self.ball_id = ball_id
        self.physx_scene = physx_scene

        actor = physx.RigidDynamic()
        actor.attach_shape(
            physx.Shape.create_sphere(2.5, physx.Material(restitution=0.75))
        )
        actor.set_global_pose(pose=(start_pos, self.start_orientation))
        actor.set_mass(1.0)
        physx_scene.add_actor(actor)

        self.actor = actor

        self.arena_object = GLTF(
            url="/store/models/soccerball.glb",
            position=swap_yz(start_pos),
            scale=(2.5, 2.5, 2.5),
            object_id=f"ball_{ball_id}",
            clickable=True,
            # evt_handler=self.click_handler,
            persist=True,
            # dynamic_body={
            #     "type": "dynamic",
            #     "mass": 1,
            #     "linearDamping": 0.03,
            #     "angularDamping": 0.03,
            #     "shape": "sphere",
            # },
        )


class SoccerGame(PhysicsSystem):
    def __init__(self, count=1, **kwargs):
        super().__init__(**kwargs)
        self.balls = []
        self.count = count
        # self.renderer = PyPhysxOffscreenRenderer()
        self.renderer = PyPhysxViewer()
        self.renderer.add_physx_scene(self.physx_scene)

    def start(self):
        for i in range(self.count):
            print("creating ball", i)
            start_pos = [random.random(), random.random(), (i + 2) * 6]
            b = SoccerBall(physx_scene=self.physx_scene, ball_id=i, start_pos=start_pos)
            self.balls.append(b)
            self.scene.add_object(b.arena_object)
        self.scene.run_async(self.step_game_async)
        super().start()

    async def step_game_async(self):
        j = 0
        while self.renderer.is_active:
            self.physx_scene.simulate(self.physx_rate.period())
            self.renderer.update()
            if j % (self.physics_rate // self.physics_push_sync_rate) == 0:
                for ball in self.balls:
                    update = {}
                    ball_pos, ball_rot = ball.actor.get_global_pose()
                    swapped_pos = swap_yz(ball_pos, 3)
                    if swapped_pos != ball.prev_pos:
                        update["position"] = swapped_pos
                        ball.prev_pos = swapped_pos
                    swapped_rot = swap_rot(as_float_array(ball_rot), 3)
                    if swapped_rot != ball.prev_rot:
                        update["rotation"] = swapped_rot
                        ball.prev_rot = swapped_rot
                    if update:
                        self.scene.update_object(ball.arena_object, **update)
            j += 1
            self.physx_rate.sleep()


game = SoccerGame(count=1)
game.start()
