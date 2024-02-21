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

# attribute example tests
tests+=("python3 examples/attributes/animation_mixer.py")
tests+=("python3 examples/attributes/animation.py")
tests+=("python3 examples/attributes/armarker.py")
tests+=("python3 examples/attributes/attribution.py")
tests+=("python3 examples/attributes/blip.py")
tests+=("python3 examples/attributes/box_collision.py")
tests+=("python3 examples/attributes/clickable.py")
tests+=("python3 examples/attributes/collision.py")
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
tests+=("python3 examples/attributes/screenshare.py")
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
tests+=("python3 examples/objects/videosphere.py")

# tutorial example tests
tests+=("python3 examples/tutorial/advanced.py")
tests+=("python3 examples/tutorial/beginner.py")
tests+=("python3 examples/tutorial/intermediate.py")
tests+=("python3 examples/tutorial/novice.py")

# example apps
tests+=("python3 examples/addtopic.py")
tests+=("python3 examples/anim-test.py")
tests+=("python3 examples/arm-demo.py -mh $host -n $namespace -s $scene")
tests+=("python3 examples/camera-child.py")
tests+=("python3 examples/camera-print.py")
tests+=("python3 examples/camera-tracer.py")
tests+=("python3 examples/chess.py -mh $host -n $namespace -s $scene")
tests+=("python3 examples/device-scene.py")
tests+=("python3 examples/device-sensor.py")
tests+=("python3 examples/earth-moon.py -mh $host -n $namespace -s $scene")
tests+=("python3 examples/earth-moon-laser.py -mh $host -n $namespace -s $scene")
tests+=("python3 examples/earth-moon-simple.py -mh $host -n $namespace -s $scene")
tests+=("python3 examples/grab.py")
tests+=("python3 examples/green-boxes.py")
tests+=("python3 examples/guac.py -mh $host -n $namespace -s $scene")
tests+=("python3 examples/hello.py")
tests+=("python3 examples/laser-pointer.py")
tests+=("python3 examples/nav.py")
tests+=("python3 examples/pinata.py")
tests+=("python3 examples/physics.py")
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

# helper scripts
tests+=("arena-py-pub --help")
tests+=("arena-py-sub -mh $host -n $namespace -s $scene")
#tests+=($"arena-py-pub -mh $host -n $namespace -s $scene -m '{"object_id": "gltf-model_Earth", "action": "create", "type": "object", "data": {"object_type": "gltf-model", "position": {"x":0, "y": 0.1, "z": 0}, "url": "store/models/Earth.glb", "scale": {"x": 5, "y": 5, "z": 5}}}'")
tests+=("arena-py-permissions")
tests+=("arena-py-signout")


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
