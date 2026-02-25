#!/bin/bash
# all-test.sh
# Launch multiple examples and tests at 5 second intervals.
# Check output at system-tests/all-test.log for errors.
# Usage: bash system-tests/all-test.sh [scene_id]

PYTHON=python

host="localhost"
export MQTTH=$host
scene="${1:-all-test}"
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
add_dir_tests "examples/scenes"
add_dir_tests "examples/tutorial"
add_dir_tests "examples/simple"
add_dir_tests "system-tests"

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

# demo example apps
tests+=("${PYTHON} examples/demos/agent-tutorial/tutorial-agent.py")
tests+=("${PYTHON} examples/demos/arm/arm-demo.py -mh $host -s $scene")
tests+=("${PYTHON} examples/demos/bosch-car/Python/BoschCar.py -mh $host -s $scene")
tests+=("${PYTHON} examples/demos/chess/chess.py -mh $host -s $scene")
tests+=("${PYTHON} examples/demos/cobot-pi/ui.py")
tests+=("${PYTHON} examples/demos/mill19/mill19-twin.py")
tests+=("${PYTHON} examples/demos/mill19/spb.py")
tests+=("${PYTHON} examples/demos/networked-physics-soccer/networked-physics-soccer.py")
tests+=("${PYTHON} examples/demos/npc/NPC.py examples/demos/npc/ArenaRobot")
tests+=("${PYTHON} examples/demos/pendulum/main.py -mh $host -s $scene")
tests+=("${PYTHON} examples/demos/pinata/pinata.py")
tests+=("${PYTHON} examples/demos/tic-tac-guac/guac.py -mh $host -s $scene")

logfile="system-tests/all-test.log"
rm -f $logfile
# launch all apps
for i in "${tests[@]}"
do
    start="--> Starting $i..."

    pfile=$(echo $i | cut -d ' ' -f 2)
    pdir=$(dirname $pfile)
    rfile=$pdir/requirements.txt

    cmd="$i"

    if test -f "$rfile"; then
        echo "Found requirements: $rfile"
        if [ -d "$pdir/.venv" ]; then
            echo "Removing stale venv in $pdir/.venv..."
            rm -rf "$pdir/.venv"
        fi
        echo "Creating venv in $pdir/.venv..."
        python3 -m venv "$pdir/.venv"

        echo "Installing requirements in $pdir/.venv..."
        "$pdir/.venv/bin/pip" install --upgrade pip --quiet
        "$pdir/.venv/bin/pip" install -r "$rfile" --quiet --upgrade
        # Install local arena-py to override any stale PyPI version
        "$pdir/.venv/bin/pip" install -e . --quiet

        # If the command uses the default python, switch to venv python
        if [[ "$i" == "$PYTHON "* ]]; then
             cmd="$pdir/.venv/bin/python ${i#$PYTHON }"
        fi
    fi

    echo $start
    echo $start >> $logfile 2>&1 &
    sh -c "$cmd" >> $logfile 2>&1 &
    pid=$(echo $!)
    sleep 5
    kill -INT $pid # ctrl-c
    stop="--> Stopping pid $pid"
    echo $stop >> $logfile 2>&1 &
done
