import time
import random
import numpy 
import paho.mqtt.client as paho
broker="oz.andrew.cmu.edu"
object_name="cube_2"
object_path="/topic/render/"

#define callback
def on_message(client, userdata, message):
    time.sleep(1)
    print("received message =",str(message.payload.decode("utf-8")))

client= paho.Client("client-001") 

######Bind function to callback
client.on_message=on_message
#####
print("connecting to broker ",broker)
client.connect(broker) 
#connect
client.loop_start() #start loop to process received messages
# client.subscribe("house/bulb1")#subscribe
print("publishing intial box")
client.publish("/topic/render/cube_2/","cube_2,0,0,0,0,0,0,0,1,1,1,#AA0000,on")

while True:
  z=1.0
  color = "#%06x" % random.randint(0, 0xFFFFFF)
  cube_str = object_name + ",{},{},{},0,0,0,0,1,1,1,{},on"

  # Walk out
  for x in numpy.arange(0.0, 20.0, 0.2):
    y=1
    z+=random.random()-0.5
    pos_str = "x:{}; y:{}; z:{};"
    client.publish(object_path+object_name,cube_str.format(x,y,z,color))
    time.sleep(0.1)

  # Walk back 
  for x in numpy.arange(20.0, 0.0, -0.2):
    y=1
    z-=random.random()-0.5
    pos_str = "x:{}; y:{}; z:{};"
    client.publish(object_path+object_name,cube_str.format(x,y,z,color))
    time.sleep(0.1)


client.disconnect() #disconnect
client.loop_stop() #stop loop
