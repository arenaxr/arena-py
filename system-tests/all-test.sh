#!/bin/bash
# all-test.sh
# Launch multiple examples and tests at 5 second intervals.
# Check output at system-tests/all-test.log for errors.

PYTHON=python

host="arena-dev1.conix.io"
export MQTTH=$host
scene="test"
export SCENE=$scene
device="robot1"
export DEVICE=$device

add_dir_tests () {
    directory_path=$1
    for file in "$directory_path"/*.py; do
        if [ -f "$file" ]; then
            tests+=("${PYTHON} $file")
        fi
    done
}

# prime with auth token
${PYTHON} -c "from arena import *; \
    Scene(host='$host',scene='$scene'); \
    Device(host='$host',device='$device');"

declare -a tests

add_dir_tests "examples/attributes"
add_dir_tests "examples/objects"
add_dir_tests "examples/callbacks"
add_dir_tests "examples/basic"
add_dir_tests "examples/tutorial"
add_dir_tests "examples/simple"
add_dir_tests "system-tests"

# demo example apps
tests+=("${PYTHON} examples/demos/agent-tutorial/tutorial-agent.py")
tests+=("${PYTHON} examples/demos/arm/arm-demo.py -mh $host -s $scene")
tests+=("${PYTHON} examples/demos/pinata/pinata.py")
tests+=("${PYTHON} examples/demos/soccer-physics/physics.py")
tests+=("${PYTHON} examples/demos/tic-tac-guac/guac.py -mh $host -s $scene")
tests+=("${PYTHON} examples/demos/chess/chess.py -mh $host -s $scene")
tests+=("${PYTHON} examples/demos/pendulum/main.py -mh $host -s $scene")
tests+=("${PYTHON} examples/demos/npc/NPC.py examples/demos/npc/ArenaRobot")
tests+=("${PYTHON} examples/demos/cobot-pi/ui.py")
tests+=("${PYTHON} examples/demos/bosch-car/Python/BoschCar.py -mh $host -s $scene")
tests+=("${PYTHON} examples/demos/mill19/mill19-twin.py")
tests+=("${PYTHON} examples/demos/mill19/spb.py")


# tool apps
tests+=("${PYTHON} tools/arb/arb.py -mh $host -s $scene --manifest tools/arb/arb-manifest.json")
tests+=("${PYTHON} tools/avatar/avatar.py")
tests+=("${PYTHON} tools/badges/badges.py")
tests+=("${PYTHON} tools/calibrate-vr/calibrate.py -mh $host -s $scene")
tests+=("${PYTHON} tools/camera-tour/camera.py")
tests+=("${PYTHON} tools/dir-sign/dir-sign.py")
tests+=("${PYTHON} tools/etc-showcase/etc-room.py")
tests+=("${PYTHON} tools/import-export-scenes/import_export.py")
tests+=("${PYTHON} tools/init3d/init3d.py")
tests+=("${PYTHON} tools/oh/oh-boards.py")
tests+=("${PYTHON} tools/poster-session/pplacement.py")
tests+=("${PYTHON} tools/questions/questions.py")
tests+=("${PYTHON} tools/spin-poster/spin-poster.py")

# helper scripts
tests+=("arena-py-pub --help")
tests+=("arena-py-sub -mh $host -s $scene")
tests+=("arena-py-pub -mh $host -s $scene -m '{\"object_id\": \"gltf-model_Earth\", \"action\": \"create\", \"type\": \"object\", \"data\": {\"object_type\": \"gltf-model\", \"position\": {\"x\":0, \"y\": 0.1, \"z\": 0}, \"url\": \"store/models/Earth.glb\", \"scale\": {\"x\": 5, \"y\": 5, \"z\": 5}}}'")
tests+=("arena-py-permissions")
tests+=("arena-py-signout")


logfile="system-tests/all-test.log"
rm -f $logfile
# launch all apps
for i in "${tests[@]}"
do
    start="--> Starting $i..."

    pfile=$(echo $i | cut -d ' ' -f 2)
    pdir=$(dirname $pfile)
    rfile=$pdir/requirements.txt
    if test -f "$rfile"; then
        echo "Installing $rfile..."
        pip3 install -r $rfile
    fi

    echo $start
    echo $start >> $logfile 2>&1 &
    sh -c "$i" >> $logfile 2>&1 &
    pid=$(echo $!)
    sleep 5
    kill -INT $pid # ctrl-c
    stop="--> Stopping pid $pid"
    echo $stop >> $logfile 2>&1 &
done
