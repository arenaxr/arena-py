from arena import *
import pybullet as p
import time
import pybullet_data
import asyncio

from typing import List

Vector = List[float]

BASE_ORIENTATION = p.getQuaternionFromEuler([0, 0, 0])


def swap_yz(pos: Vector, round_decimals: int = None):
    """
    Util to swap y and z axis, where AFrame uses y as vertical, pybullet uses z.
    :param pos: Array-like of len 3
    :param round_decimals: int, defaults to None (no rounding), optional
    :return: list
    """
    if round_decimals is not None:
        return [
            round(pos[0], round_decimals),
            round(pos[2], round_decimals),
            round(pos[1], round_decimals),
        ]
    else:
        return [pos[0], pos[2], pos[1]]


def swap_rot(rot: Vector, round_decimals: int = None):
    """
    Util to swap y and z axis, where AFrame uses y as vertical, pybullet uses z.
    Also negates the rotation for yet unknown reason
    :param rot: Array-like of len 4
    :param round_decimals: int, defaults to None (no rounding), optional
    :return: list
    """
    if round_decimals is not None:
        return [
            round(rot[0], round_decimals),
            round(rot[2], round_decimals),
            round(rot[1], round_decimals),
            round(rot[3], round_decimals),
        ]
    else:
        return [-rot[0], -rot[2], -rot[1], rot[3]]


class PhysicsSystem:
    """
    Physics system based on pybullet
    """

    def __init__(
        self,
        physics_rate=60,  # Default pybullet step = 1/240s
        physics_update_rate=30, # Lower than engine rate
        physics_push_sync_rate=1,  # Frequency of mqtt object_updates pushes
        mqtt_sync_rate=60,  # Frequency of physics sync to mqtt object states
        gravity=-9.8,  # Gravity of physics system
        **kwargs,
    ):
        self.physics_rate = physics_rate
        self.physics_interval = 1 / physics_rate
        self.physics_update_rate = physics_update_rate
        self.physics_push_sync_rate = physics_push_sync_rate
        self.mqtt_sync_rate = mqtt_sync_rate

        self.physicsClient = p.connect(p.DIRECT)
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0, 0, gravity)
        p.setTimeStep(self.physics_interval)

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

        self.plane_id = p.loadURDF("plane.urdf", 0, 0, -0.01)
        p.changeDynamics(self.plane_id, -1, restitution=0.75, mass=0)
        self.scene.add_object(
            Box(
                position=[0, 0.01, 0],
                scale=[120, 0.01, 80],
                object_id="grass",
                persist=True,
                material=Material(color=(49, 114, 41)),
            )
        )

    def start(self):
        self.scene.run_async(self.sync_world)
        self.scene.run_tasks()

    def new_user_handler(self, _scene, obj, _payload):
        """
        Model users as 0.5m static spheres
        :param _scene:
        :param obj:
        :param _payload:
        :return:
        """
        d = obj.data
        new_sphere = p.loadURDF(
            "sphere2.urdf", [d.position.x, d.position.z, d.position.y]
        )
        p.changeDynamics(
            new_sphere,
            -1,
            restitution=0.75,
            mass=0,
            lateralFriction=1,
            localInertiaDiagonal=(0, 0, 0),
        )
        self.user_cams[obj.object_id] = {
            "phys_id": new_sphere,
            "timestamp": time.time(),
        }

    def left_user_handler(self, _scene, obj, _payload):
        if self.user_cams.get(obj.object_id):
            p.removeBody(self.user_cams.pop(obj.object_id)["phys_id"])

    async def sync_world(self):
        while True:
            for c in self.user_cams.items():
                scene_user = self.scene.users.get(c[0])
                if scene_user:
                    new_pos = [
                        scene_user.data.position.x,
                        scene_user.data.position.z,
                        scene_user.data.position.y,
                    ]
                    update_sphere_id = c[1]["phys_id"]
                    prev_pos, _ = p.getBasePositionAndOrientation(update_sphere_id)
                    if new_pos != list(prev_pos):
                        p.resetBasePositionAndOrientation(
                            update_sphere_id, new_pos, BASE_ORIENTATION
                        )
            await asyncio.sleep(1 / self.mqtt_sync_rate)


# TODO: Make generic phys-arena object class
class SoccerBall:
    def __init__(self, system, ball_id: int, start_pos: Vector = None):
        if start_pos is None:
            start_pos = [0, 0, 3]  # Start slightly above size of ball
        self.start_pos = start_pos
        self.start_orientation = p.getQuaternionFromEuler([0, 0, 0])
        self.ball_id = ball_id
        self.physics_system = system

        self.physics_id = p.loadURDF(
            "soccerball.urdf", start_pos, self.start_orientation, globalScaling=2.5
        )
        p.changeDynamics(self.physics_id, -1, restitution=0.75)
        self.arena_object = GLTF(
            url="https://xr.andrew.cmu.edu/models/soccerball.gltf",
            position=swap_yz(start_pos),
            scale=(2.5, 2.5, 2.5),
            object_id=f"ball_{ball_id}",
            clickable=True,
            evt_handler=self.click_handler,
            persist=True,
            dynamic_body={"type":"dynamic", "mass":1,  "linearDamping":0.03,
                          "angularDamping":0.03, "shape": "sphere"}
        )

    def click_handler(self, _scene, evt, _msg):
        if evt.type == "mousedown":
            p.resetBasePositionAndOrientation(
                self.physics_id, self.start_pos, self.start_orientation
            )
            p.stepSimulation()
            self.physics_system.push_physics_update(self)


class SoccerGame(PhysicsSystem):
    def __init__(self, count=1, **kwargs):
        super().__init__(**kwargs)
        self.balls = []
        self.count = count

    def start(self):
        for i in range(self.count):
            print("creating ball", i)
            start_pos = [random.random(), random.random(), (i+1) * 6]
            b = SoccerBall(system=self, ball_id=i, start_pos=start_pos)
            self.balls.append(b)
            self.scene.add_object(b.arena_object)
        self.scene.run_async(self.step_game_async)
        super().start()

    def push_physics_update(self, ball: SoccerBall):
        p_id = ball.physics_id
        lin_v, ang_v = p.getBaseVelocity(p_id)
        ball_pos, ball_rot = p.getBasePositionAndOrientation(p_id)
        self.scene.generate_physics_event(
            obj=ball.arena_object,
            position=swap_yz(ball_pos, round_decimals=3),
            rotation=swap_yz(ball_rot, round_decimals=3),
            linear_velocity=swap_yz(lin_v, round_decimals=3),
            angular_velocity=swap_yz(ang_v, round_decimals=3),
        )

    async def step_game_async(self):
        j = 0
        prev_collisions = set()
        collisions = set()
        push_updates = set()
        prev_sleep_delay = 0
        while True:
            loop_start = time.time()
            p.stepSimulation()
            b1_pos, _ = p.getBasePositionAndOrientation(0)
            for ball in self.balls:
                for c in p.getContactPoints(ball.physics_id):
                    if c[2] != self.plane_id:
                        collisions.add(ball)
            for prev_ball in prev_collisions:
                if prev_ball not in collisions:
                    push_updates.add(prev_ball)
            prev_collisions = collisions.copy()
            collisions.clear()
            if j % (self.physics_rate // self.physics_push_sync_rate) == 0:
                for ball in self.balls:
                    self.push_physics_update(ball)
                    ball_pos, ball_rot = p.getBasePositionAndOrientation(ball.physics_id)
                    self.scene.update_object(
                        ball.arena_object,
                        position=swap_yz(ball_pos),
                        rotation=swap_rot(ball_rot),
                    )
            elif j % (self.physics_rate // self.physics_update_rate) == 0:
                for ball in push_updates:
                    self.push_physics_update(ball)
                push_updates.clear()
            j += 1
            loop_end = time.time()
            await asyncio.sleep(
                self.physics_interval - (loop_end - loop_start) - prev_sleep_delay,
            )
            prev_sleep_delay = max(0.0, time.time() - loop_end - self.physics_interval)


game = SoccerGame(count=2)
game.start()
