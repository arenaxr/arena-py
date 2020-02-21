import sys

sys.path.append("../")
import time
import arena

arena.init("oz.andrew.cmu.edu", "realm", "demo")

arena.start()

# Draw origin cube
scale = (0.1, 0.1, 0.1)
color = (255, 0, 0)
location = (0, 0, 0)
originCube = arena.Object(persist=True, location=location, scale=scale, color=color)

# Draw UWB tag locations
color = (255, 0, 0)
location = (-2.183, 1.407, -6.194)
arena.Object(persist=True, location=location, scale=scale, color=color)

color = (0, 255, 0)
location = (-1.739, 1.159, -6.155)
arena.Object(persist=True,  location=location, scale=scale, color=color)

color = (0, 0, 255)
location = (-2.229, 0.280, -6.011)
arena.Object(persist=True,  location=location, scale=scale, color=color)

color = (0, 255, 255)
location = (-1.242, 0.287, -5.970)
arena.Object(persist=True,  location=location, scale=scale, color=color)

# UWB
color = (255, 255, 0)
location = (2.185, 2.282, -5.033)
arena.Object(persist=True,  location=location, scale=scale, color=color)

color = (255, 255, 0)
location = (2.175, 0.712, 0.027)
arena.Object(persist=True,  location=location, scale=scale, color=color)

color = (255, 255, 0)
location = (-0.238, 1.471, -4.868)
arena.Object(persist=True,  location=location, scale=scale, color=color)

color = (255, 255, 0)
location = (-3.382, 1.407, -0.387)
arena.Object(persist=True,  location=location, scale=scale, color=color)

arena.handle_events()
arena.stop()
