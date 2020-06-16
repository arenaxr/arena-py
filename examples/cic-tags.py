import sys
import time
import arena

arena.init("oz.andrew.cmu.edu", "realm", "cic-tags")

# Draw origin cube
rotation = (0.0, 0.0, 0.0, 0.0)
scale = (0.15, 0.02, 0.15)
color = (255, 0, 0)
location = (0, 0, 0)
originCube = arena.Object(location=location, rotation=rotation, scale=scale, color=color)


# Draw April tag locations
location = (1.079, 0.789, 0.071)
rotation = (0.0, 0.0, 0.0, 0.0)
scale = (0.15, 0.15, 0.02)
color = (0, 255, 0)
arena.Object(location=location, rotation=rotation, scale=scale, color=color)

print( "View scene at URL: https://xr.andrew.cmu.edu/?scene=cic-tags" )
print( "Note, tags set wouth persist so open browser before running." )

arena.handle_events()
