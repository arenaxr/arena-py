#!/bin/bash
# all-test.sh
# Launch multiple examples and tests at 5 second intervals.
# Check ouput at system-tests/all-test.log for errors.

host="arenaxr.org"
export MQTTH=$host
scene="test"
export SCENE=$scene
device="robot1"
export DEVICE=$device

namespace="whatismynamespace" # TODO: user-defined
export NAMESPACE=$namespace

# prime with auth token
python3 -c "from arena import *; \
    Scene(host='$host',namespace='$namespace',scene='$scene'); \
    Device(host='$host',namespace='$namespace',device='$device');"

declare -a tests

# example apps
tests+=("python3 examples/addtopic.py")
tests+=("python3 examples/anim-test.py")
tests+=("python3 examples/arm-demo.py -mh $host -n $namespace -s $scene")
tests+=("python3 examples/camera-child.py")
tests+=("python3 examples/camera-print.py")
tests+=("python3 examples/camera-tracer.py")
tests+=("python3 examples/device-scene.py")
tests+=("python3 examples/device-sensor.py")
tests+=("python3 examples/earth-moon.py -mh $host -n $namespace -s $scene")
tests+=("python3 examples/green-boxes.py")
tests+=("python3 examples/guac.py -mh $host -n $namespace -s $scene")
tests+=("python3 examples/hello.py")
tests+=("python3 examples/laser-pointer.py")
tests+=("python3 examples/nav.py")
tests+=("python3 examples/pinata.py")
tests+=("python3 examples/sound-control.py")
tests+=("python3 examples/statue.py -mh $host -n $namespace -s $scene")
tests+=("python3 examples/teleporter.py")
tests+=("python3 examples/tutorial-agent.py")

# system-test apps
tests+=("python3 system-tests/auto-updates-helper.py")
tests+=("python3 system-tests/auto-updates.py")
tests+=("python3 system-tests/balls.py")
tests+=("python3 system-tests/custom-topic.py")
tests+=("python3 system-tests/errors.py")
tests+=("python3 system-tests/get-persisted-objs.py")
tests+=("python3 system-tests/headbanger.py")
tests+=("python3 system-tests/move-camera.py")
tests+=("python3 system-tests/move-cubes.py")
tests+=("python3 system-tests/persist1-create.py")
tests+=("python3 system-tests/persist2-discover.py")
tests+=("python3 system-tests/rotate-cube.py")
tests+=("python3 system-tests/scene-callbacks.py")
tests+=("python3 system-tests/tasks.py")
tests+=("python3 system-tests/trans-cubes.py")
tests+=("python3 system-tests/user-callbacks.py")

logfile="system-tests/all-test.log"
rm -f $logfile
# launch all apps
for i in "${tests[@]}"
do
    start="-------------------------------> Starting $i..."
    echo $start
    echo $start >> $logfile 2>&1 &
    sh -c "$i" >> $logfile 2>&1 &
    pid=$(echo $!)
    sleep 5
    kill -INT $pid # ctrl-c
    stop="-------------------------------> Stopping pid $pid"
    echo $stop >> $logfile 2>&1 &
done
