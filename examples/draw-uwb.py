import sys
import time
import arena

arena.init("oz.andrew.cmu.edu", "realm", "render")

# Draw origin cube
rotation = (0.0, 0.0, 0.0, 0.0)
scale = (0.1, 0.1, 0.1)
color = (255, 0, 0)
location = (0, 0, 0)
originCube = arena.Object(location=location, rotation=rotation, scale=scale, color=color)
color = (0, 255, 0)

# Draw UWB tag locations
location = (1.079, 0.789, 0.071)
arena.Object(location=location, rotation=rotation, scale=scale, color=color)
location = (1.079, 0.789, 0.778)
arena.Object(location=location, rotation=rotation, scale=scale, color=color)
location = (2.674, 0.789, 0.071)
arena.Object(location=location, rotation=rotation, scale=scale, color=color)
location = (2.674, 0.789, 0.778)
arena.Object(location=location, rotation=rotation, scale=scale, color=color)

arena.handle_events()
