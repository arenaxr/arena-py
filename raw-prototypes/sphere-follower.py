import time
import random
import numpy 
import paho.mqtt.client as mqtt
import signal
import sys




mqtt_broker="oz.andrew.cmu.edu"
scene_path="/topic/render/"
object_name="sphere_y"

# Object starting point, global so click handler can modify it
x=5.0
y=5.0
z=1.0
chaser=False

def signal_handler(sig, frame):
  client.publish(scene_path+object_name,"",retain=True)  
  print("Removing objects before I quit...")
  time.sleep(1)	
  sys.exit(0)


#define callbacks
def on_click_input(client, userdata, msg):
    global x
    global y
    global z
    global chaser
    print("got click: %s \"%s\"" % (msg.topic, msg.payload))
    click_x,click_y,click_z,user = msg.payload.split(',')
    print( "Clicked by: " + user )
    obj_x=float(x)-float(click_x)
    obj_y=float(y)-float(click_y)
    obj_z=float(z)-float(click_z)
    if str(msg.topic).find("mousedown") != -1 and chaser==False:
      print( "Obj relative click: " + str(obj_x) + "," + str(obj_y) + "," + str(obj_z) )
      client.subscribe(scene_path+user)
      client.message_callback_add(scene_path+user, on_camera)
      chaser=True
      color = "#00FF00"
      cube_str = object_name + ",{},{},{},0,0,0,0,1,1,1,{},on"
      client.publish(scene_path+object_name,cube_str.format(x,y,z,color),retain=True)
    else:
        client.unsubscribe(scene_path+user)
        print( "Unsubscribing from camera")
        chaser=False
        color = "#FF0000"
        cube_str = object_name + ",{},{},{},0,0,0,0,1,1,1,{},on"
        client.publish(scene_path+object_name,cube_str.format(x,y,z,color),retain=True)

   

# /topic/render/camera_7452_X camera_7452_X,-9.979,1.600,-2.760,-0.062,-0.855,-0.105,0.504,0,0,0,#8e1191,on
def on_camera(client, userdata, msg):
    global x
    global y
    global z
    print("got camera: %s \"%s\"" % (msg.topic, msg.payload))
    t,cam_x,cam_y,cam_z, t, t, t, t, t, t, t, t, t, t = msg.payload.split(',')
    print( cam_x,cam_y,cam_z)
    x=str(float(cam_x)+3.0)
    y=cam_y
    z=cam_z
   


client= mqtt.Client("client-002", clean_session=True, userdata=None ) 


print("connecting to broker ",mqtt_broker)
client.connect(mqtt_broker) 

client.subscribe(scene_path+object_name+"/mousedown")
client.message_callback_add(scene_path+object_name+"/mousedown", on_click_input)



############
# Setup box
# Delete the object from the scene to get a fresh start with a null message
client.publish(scene_path+object_name,"")  
#color = "#%06x" % random.randint(0, 0xFFFFFF)
color = "#FF0000"
cube_str = object_name + ",{},{},{},0,0,0,0,1,1,1,{},on"
# Publish a cube with x,y,z and color parameters
# retain=True makes it persistent
client.publish(scene_path+object_name,cube_str.format(x,y,z,color),retain=True)

# Enable click listener for object (allows it to be clickable)
client.publish(scene_path+object_name+"/click-listener","enable",retain=True)

client.loop_start() #start loop to process received mqtt messages
# add signal handler to remove objects on quit
signal.signal(signal.SIGINT, signal_handler)

# Main loop that runs every 5 seconds and changes the object color
while True:
    print("Main chaser loop" )
    cube_str = "property: position; to: {} {} {}; dur: 1000; easing: linear"
    # Publish an animation command to move the object
    client.publish(scene_path+object_name+"/animation",cube_str.format(x,y,z))
    time.sleep(1.0)

client.disconnect() #disconnect
client.loop_stop() #stop loop
