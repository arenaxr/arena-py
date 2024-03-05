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

# define apps
chess="python3 examples/demos/chess/chess.py -mh $host -n $namespace' -s $scene -p 1.5 0 -1.5 -r 0 45 0 -c .15 .15 .15"
cobot="python3 examples/demos/cobot-pi/ui.py -mh $host -n $namespace' -s $scene -p -2 .8 -3 -r 0 0 0 -c 1 1 1"
npc_arena="python3 examples/demos/npc/NPC.py -mh $host -n $namespace'-s $scene -p 7.2 0 -2.8 -r 0 0 0 -c .8 .8 .8 -config NPCs/config.json"
npc_appollo_bolden="python3 examples/demos/npc/NPC.py -mh $host -n $namespace'-s $scene -p 7.2 0 -2.8 -r 0 0 0 -c .8 .8 .8 -config NPC_ApolloBolden/config.json"
npc_appollo_capsule="python3 examples/demos/npc/NPC.py -mh $host -n $namespace'-s $scene -p 7.2 0 -2.8 -r 0 0 0 -c .8 .8 .8 -config NPC_ApolloCapsule/config.json"
npc_bosch="python3 examples/demos/npc/NPC.py -mh $host -n $namespace'-s $scene -p 7.2 0 -2.8 -r 0 0 0 -c .8 .8 .8 -config NPC_BoschCar/config.json"
npc_video_only="python3 examples/demos/npc/NPC.py -mh $host -n $namespace'-s $scene -p 7.2 0 -2.8 -r 0 0 0 -c .8 .8 .8 -config NPC_VideoOnly/config.json"

# launch all apps
# Press Ctrl+C to kill them all
sh -c "$chess & $cobot& $npc_arena & wait"
# parameters to run demos in the arena main demo scene
