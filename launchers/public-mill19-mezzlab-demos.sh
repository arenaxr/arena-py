#!/bin/bash
# Launch multiple programs per scene

host="arenaxr.org"
namespace="public"
scene="mill19-mezzlab"

export MQTTH=$host
export NAMESPACE=$namespace
export SCENE=$scene

# prime auth
python3 -c "from arena import *; Scene(host='$host',namespace='$namespace',scene='$scene')"

# run from anywhere
laser="python3 examples/simple/laser-pointer.py"
spb="python3 examples/demos/mill19/spb.py"

# launch all apps
# Press Ctrl+C to kill them all
sh -c "$spb & $laser & wait"
