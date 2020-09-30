# balls.py
#
import arena
arena.init("arena.andrew.cmu.edu", "realm", "examples")
arena.Object(objType=arena.Shape.cone, location=(1, 0, -3))
arena.handle_events()
