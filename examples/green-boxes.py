import sys
sys.path.append('../')
import time
import random
import numpy 
import arena



arena.init("oz.andrew.cmu.edu","realm/s/render")

arena.start()

location=(5.0,6.0,7.0)
rotation=(0.0,0.0,0.0,0.0)
color=(0,255,0)
scale=(1.0,1.0,1.0)

# Create a box
myCube = arena.cube(location,rotation,scale,color)
# Delete a box
del myCube

x=1.0

while True: 
  # Create a bunch of boxes drawn directly to screen
  arena.cube((random.randrange(10),random.randrange(10),random.randrange(10)),rotation,scale,color)
  x=x+1
  time.sleep(.5)




arena.stop()

