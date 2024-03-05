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
statue="python3 examples/simple/statue.py -mh $host -n $namespace -s $scene -p 0 0 0 -r 0 0 0 -s 0 0 0"
laser="python3 examples/simple/laser-pointer.py"
green="python3 examples/simple/green-boxes.py"
pinata="python3 examples/demos/pinata/pinata.py"
earth="python3 examples/simple/earth-moon.py -mh $host -n $namespace -s $scene -p 0 0.5 0  -r 0 0 0   -c 0.25 0.25 0.25"
robot="python3 examples/demos/arm/arm-demo.py -mh $host -n $namespace -s $scene   -p -0.5 0.2 -2.75  -r 0 0 0   -c 0.25 0.25 0.25"
guac="python3 examples/demos/tic-tac-guac/guac.py -mh $host -n $namespace -s $scene        -p 0.75 0.5 0 -r 0 180 0   -c 0.5 0.5 0.5"

# launch all apps
# Press Ctrl+C to kill them all
sh -c "$robot & $guac & wait"
