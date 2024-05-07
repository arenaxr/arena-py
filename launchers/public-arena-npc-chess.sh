#!/bin/bash
# Launch multiple programs per scene

host="arenaxr.org"
namespace="public"
scene="arena"

export MQTTH=$host
export NAMESPACE=$namespace
export SCENE=$scene

# prime auth
python3 -c "from arena import *; Scene(host='$host',namespace='$namespace',scene='$scene')"

# run from anywhere
chess="python3 examples/demos/chess/chess.py -mh $host -n $namespace -s $scene -p 1.5 0 -1.5 -r 0 45 0 -c .15 .15 .15"
cobot="python3 examples/demos/cobot-pi/MyCobotPi320.py"
npc_arena="python3 examples/demos/npc/NPC.py examples/demos/npc/ArenaRobot"

# run from rpi
cobot_rpi="bash examples/demos/cobot-pi/autostart_python.sh"

# run from arduno connected to COM4
car_arduino="python3 examples/demos/bosch-car/Python/BoschCar.py"

# launch all apps
# Press Ctrl+C to kill them all
sh -c "$chess & $cobot& $npc_arena & wait"
# parameters to run demos in the arena main demo scene
