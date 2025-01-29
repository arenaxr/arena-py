import time
import sys
from datetime import datetime

class SceneState():

    DFT_INACTIVE_TIME_SECS=3600

    def __init__(self, scene=None, inactive_callback=None, inactive_time_secs=DFT_INACTIVE_TIME_SECS, active_on_new_users=False, exit_on_inactive=True):
        self.scene = scene
        self.inactive_callback = inactive_callback
        self.inactive_time_secs = inactive_time_secs
        self.users_cam = dict()
        self._active = True
        self._active_ts = datetime.now()
        self.active_on_new_users = active_on_new_users
        self.exit_on_inactive = exit_on_inactive

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, value):
        self._active = value
        self._active_ts = datetime.now()

    def set_scene(self, scene):
        self.scene = scene

    def user_joined(self, camera):
        user_cam = UserCameraState(camera)
        self.users_cam[user_cam.id] = user_cam
        if self.active_on_new_users: self.active = True

    def user_left(self, id):
        user_cam = self.users_cam[id]
        self.users_cam.pop(user_cam.id)
        return user_cam

    def list_users(self):
        return self.users_cam.items()

    def update(self):
        active_users = False
        for id, user_cam in self.users_cam.items():
           active_users = active_users or user_cam.update_state()

        if self.active:
            if active_users: self.active = True

            dif = (datetime.now() - self._active_ts).total_seconds()
            if dif > self.inactive_time_secs: 
                self.active = False
                if self.inactive_callback: self.inactive_callback(self.scene)
        else:
            if self.exit_on_inactive:
                if self.scene: self.scene.exit()
                else: sys.exit(0)


def scene_inactive_callback(scene):
    print("Inactive!")
    if not scene: return
    print()

class UserCameraState:

  DFT_INACTIVE_TIME_SECS=600

  def __init__(self, camera, inactive_time_secs=DFT_INACTIVE_TIME_SECS):
    self.id = camera.object_id
    self.camera = camera
    self.prev_pos = None
    self.active = True
    self.active_ts = datetime.now()
    self.inactive_time_secs = inactive_time_secs

  def curr_pos(self):
    return self.camera.data.position

  def moved(self, min_displacement=0.5, update_pos=True):
    displacement = 0
    if self.prev_pos:
      displacement = self.prev_pos.distance_to(self.curr_pos())
    if (update_pos): self.prev_pos = self.curr_pos()
    if (displacement > min_displacement): return True     
    return False

  def update_state(self):
    if self.moved():
      self.active = True
      self.active_ts = datetime.now()

    if (self.active):
      dif = (datetime.now() - self.active_ts).total_seconds()
      if dif > self.inactive_time_secs: 
        self.active = False

    return self.active

