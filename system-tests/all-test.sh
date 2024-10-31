#!/bin/bash
# all-test.sh
# Launch multiple examples and tests at 5 second intervals.
# Check ouput at system-tests/all-test.log for errors.

host="arena-dev1.conix.io"
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

# attribute example tests
tests+=("python3 examples/attributes/animation_mixer.py")
tests+=("python3 examples/attributes/animation.py")
tests+=("python3 examples/attributes/armarker.py")
tests+=("python3 examples/attributes/attribution.py")
tests+=("python3 examples/attributes/blip.py")
tests+=("python3 examples/attributes/box_collision.py")
tests+=("python3 examples/attributes/clickable.py")
tests+=("python3 examples/attributes/color.py")
tests+=("python3 examples/attributes/goto_landmark.py")
tests+=("python3 examples/attributes/goto_url.py")
tests+=("python3 examples/attributes/jitsi_video.py")
tests+=("python3 examples/attributes/landmark.py")
tests+=("python3 examples/attributes/look_at.py")
tests+=("python3 examples/attributes/material_extras.py")
tests+=("python3 examples/attributes/material.py")
tests+=("python3 examples/attributes/model_lod.py")
tests+=("python3 examples/attributes/modelUpdate.py")
tests+=("python3 examples/attributes/morph.py")
tests+=("python3 examples/attributes/multisrc.py")
tests+=("python3 examples/attributes/particles.py")
tests+=("python3 examples/attributes/physics_impulse.py")
tests+=("python3 examples/attributes/position.py")
tests+=("python3 examples/attributes/rotation.py")
tests+=("python3 examples/attributes/scale.py")
tests+=("python3 examples/attributes/shadow.py")
tests+=("python3 examples/attributes/sound.py")
tests+=("python3 examples/attributes/text_input.py")
tests+=("python3 examples/attributes/video_control.py")

# object example tests
tests+=("python3 examples/objects/box.py")
tests+=("python3 examples/objects/capsule.py")
tests+=("python3 examples/objects/circle.py")
tests+=("python3 examples/objects/cone.py")
tests+=("python3 examples/objects/cylinder.py")
tests+=("python3 examples/objects/dodecahedron.py")
tests+=("python3 examples/objects/entity.py")
tests+=("python3 examples/objects/gltf.py")
tests+=("python3 examples/objects/hands.py")
tests+=("python3 examples/objects/icosahedron.py")
tests+=("python3 examples/objects/image.py")
tests+=("python3 examples/objects/light.py")
tests+=("python3 examples/objects/line.py")
tests+=("python3 examples/objects/obj_model.py")
tests+=("python3 examples/objects/ocean.py")
tests+=("python3 examples/objects/octahedron.py")
tests+=("python3 examples/objects/pcd.py")
tests+=("python3 examples/objects/plane.py")
tests+=("python3 examples/objects/ring.py")
tests+=("python3 examples/objects/roundedbox.py")
tests+=("python3 examples/objects/sphere.py")
tests+=("python3 examples/objects/splat.py")
tests+=("python3 examples/objects/tetrahedron.py")
tests+=("python3 examples/objects/text.py")
tests+=("python3 examples/objects/thickline.py")
tests+=("python3 examples/objects/threejs_scene.py")
tests+=("python3 examples/objects/torus_knot.py")
tests+=("python3 examples/objects/torus.py")
tests+=("python3 examples/objects/triangle.py")
tests+=("python3 examples/objects/ui.py")
tests+=("python3 examples/objects/urdf.py")
tests+=("python3 examples/objects/videosphere.py")

# tutorial example tests
tests+=("python3 examples/tutorial/advanced.py")
tests+=("python3 examples/tutorial/beginner.py")
tests+=("python3 examples/tutorial/intermediate.py")
tests+=("python3 examples/tutorial/novice.py")

# simple example apps
tests+=("python3 examples/simple/addtopic.py")
tests+=("python3 examples/simple/anim-test.py")
tests+=("python3 examples/simple/camera-child.py")
tests+=("python3 examples/simple/camera-print.py")
tests+=("python3 examples/simple/camera-tracer.py")
tests+=("python3 examples/simple/device-scene.py")
tests+=("python3 examples/simple/device-sensor.py")
tests+=("python3 examples/simple/earth-moon-laser.py")
tests+=("python3 examples/simple/earth-moon-simple.py")
tests+=("python3 examples/simple/earth-moon.py -mh $host -n $namespace -s $scene")
tests+=("python3 examples/simple/grab.py")
tests+=("python3 examples/simple/grab2.py")
tests+=("python3 examples/simple/green-boxes.py")
tests+=("python3 examples/simple/hello.py")
tests+=("python3 examples/simple/laser-pointer.py")
tests+=("python3 examples/simple/nav.py")
tests+=("python3 examples/simple/sound-control.py -mh $host -n $namespace -s $scene")
tests+=("python3 examples/simple/statue.py -mh $host -n $namespace -s $scene")
tests+=("python3 examples/simple/teleporter.py")

# demo example apps
tests+=("python3 examples/demos/agent-tutorial/tutorial-agent.py")
tests+=("python3 examples/demos/arm/arm-demo.py -mh $host -n $namespace -s $scene")
tests+=("python3 examples/demos/pinata/pinata.py")
tests+=("python3 examples/demos/soccer-physics/physics.py")
tests+=("python3 examples/demos/tic-tac-guac/guac.py -mh $host -n $namespace -s $scene")
tests+=("python3 examples/demos/chess/chess.py -mh $host -n $namespace -s $scene")
tests+=("python3 examples/demos/pendulum/main.py -mh $host -n $namespace -s $scene")
tests+=("python3 examples/demos/npc/NPC.py examples/demos/npc/ArenaRobot")
tests+=("python3 examples/demos/cobot-pi/ui.py")
tests+=("python3 examples/demos/bosch-car/Python/BoschCar.py -mh $host -n $namespace -s $scene")
tests+=("python3 examples/demos/mill19/mill19-twin.py")
tests+=("python3 examples/demos/mill19/spb.py")

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

# tool apps
tests+=("python3 tools/arb/arb.py -mh $host -n $namespace -s $scene --manifest tools/arb/arb-manifest.json")
tests+=("python3 tools/avatar/avatar.py")
tests+=("python3 tools/badges/badges.py")
tests+=("python3 tools/calibrate-vr/calibrate.py -mh $host -n $namespace -s $scene")
tests+=("python3 tools/camera-tour/camera.py")
tests+=("python3 tools/dir-sign/dir-sign.py")
tests+=("python3 tools/etc-showcase/etc-room.py")
tests+=("python3 tools/import-export-scenes/import_export.py")
tests+=("python3 tools/init3d/init3d.py")
tests+=("python3 tools/oh/oh-boards.py")
tests+=("python3 tools/poster-session/pplacement.py")
tests+=("python3 tools/questions/questions.py")
tests+=("python3 tools/spin-poster/spin-poster.py")

# helper scripts
tests+=("arena-py-pub --help")
tests+=("arena-py-sub -mh $host -n $namespace -s $scene")
tests+=("arena-py-pub -mh $host -n $namespace -s $scene -m '{\"object_id\": \"gltf-model_Earth\", \"action\": \"create\", \"type\": \"object\", \"data\": {\"object_type\": \"gltf-model\", \"position\": {\"x\":0, \"y\": 0.1, \"z\": 0}, \"url\": \"store/models/Earth.glb\", \"scale\": {\"x\": 5, \"y\": 5, \"z\": 5}}}'")
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
