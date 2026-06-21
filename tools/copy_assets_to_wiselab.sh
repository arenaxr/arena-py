#!/usr/bin/env bash
# Copy legacy example assets into the centralized wiselab store.
# Run from the `store` directory on the server filesystem.

set -euo pipefail

copy_item() {
    local src="$1"
    local dst="$2"

    if [[ ! -e "$src" ]]; then
        echo "MISSING: $src"
        return 1
    fi

    mkdir -p "$(dirname "$dst")"

    if [[ -d "$src" ]]; then
        cp -a "$src"/. "$dst"/
    else
        cp -a "$src" "$dst"
    fi
    echo "COPIED : $src -> $dst"
}

missing=0
while IFS=$'\t' read -r src dst; do
    [[ -z "$src" ]] && continue
    if ! copy_item "$src" "$dst"; then
        ((missing++))
    fi
done <<'EOF'
users/johnchoi/Characters/RobotBuddy/RobotBuddyBlue.glb	users/wiselab/Characters/RobotBuddy/RobotBuddyBlue.glb
users/johnchoi/Characters/RobotBuddy/RobotBuddyBlue.png	users/wiselab/Characters/RobotBuddy/RobotBuddyBlue.png

users/johnchoi/Sounds/NPC/Next.wav	users/wiselab/Sounds/NPC/Next.wav
users/johnchoi/Sounds/NPC/Choice.wav	users/wiselab/Sounds/NPC/Choice.wav
users/johnchoi/Sounds/NPC/Enter.wav	users/wiselab/Sounds/NPC/Enter.wav
users/johnchoi/Sounds/NPC/Exit.wav	users/wiselab/Sounds/NPC/Exit.wav
users/johnchoi/Sounds/NPC/Talking.wav	users/wiselab/Sounds/NPC/Talking.wav
users/johnchoi/Sounds/NPC/Walking.wav	users/wiselab/Sounds/NPC/Walking.wav
users/johnchoi/Sounds/jingle.wav	users/wiselab/Sounds/jingle.wav

users/johnchoi/Images/doge.jpg	users/wiselab/Images/doge.jpg
users/johnchoi/Images/dragon.jpg	users/wiselab/Images/dragon.jpg
users/johnchoi/Images/exclamation.png	users/wiselab/Images/exclamation.png
users/johnchoi/Images/fish.jpg	users/wiselab/Images/fish.jpg
users/johnchoi/Images/forest.jpg	users/wiselab/Images/forest.jpg
users/johnchoi/Images/graph.png	users/wiselab/Images/graph.png
users/johnchoi/Images/meme.jpg	users/wiselab/Images/meme.jpg
users/johnchoi/Images/nyan.jpg	users/wiselab/Images/nyan.jpg
users/johnchoi/Images/potato.jpg	users/wiselab/Images/potato.jpg
users/johnchoi/Images/question.png	users/wiselab/Images/question.png
users/johnchoi/Images/stonks.png	users/wiselab/Images/stonks.png
users/johnchoi/Images/sushi.jpg	users/wiselab/Images/sushi.jpg
users/johnchoi/Images/xr-logo.png	users/wiselab/Images/xr-logo.png
users/johnchoi/Images/yarn.jpg	users/wiselab/Images/yarn.jpg

users/johnchoi/Videos/ARENA/20200707_ARENA - A Collaborative Mixed Reality Environment.mp4	users/wiselab/Videos/ARENA/20200707_ARENA - A Collaborative Mixed Reality Environment.mp4
users/johnchoi/Videos/ARENA/20200819_ARENA Collaborative AR Authoring Tool Demo.mp4	users/wiselab/Videos/ARENA/20200819_ARENA Collaborative AR Authoring Tool Demo.mp4
users/johnchoi/Videos/ARENA/20200819_ARENA Indoor Location Tracking Demo.mp4	users/wiselab/Videos/ARENA/20200819_ARENA Indoor Location Tracking Demo.mp4
users/johnchoi/Videos/ARENA/20200819_ARENA Micro-UAV Swarm Control.mp4	users/wiselab/Videos/ARENA/20200819_ARENA Micro-UAV Swarm Control.mp4
users/johnchoi/Videos/ARENA/20200819_ARENA One Minute Madness.mp4	users/wiselab/Videos/ARENA/20200819_ARENA One Minute Madness.mp4
users/johnchoi/Videos/ARENA/20200819_ARENA Physical Object Capture (Digital Twin).mp4	users/wiselab/Videos/ARENA/20200819_ARENA Physical Object Capture (Digital Twin).mp4
users/johnchoi/Videos/ARENA/20200819_ARENA Real-Time Face Performance Capture.mp4	users/wiselab/Videos/ARENA/20200819_ARENA Real-Time Face Performance Capture.mp4
users/johnchoi/Videos/ARENA/20200819_ARENA Robot's First Steps.mp4	users/wiselab/Videos/ARENA/20200819_ARENA Robot's First Steps.mp4
users/johnchoi/Videos/ARENA/20200819_ARENA Virtual Robot Arm.mp4	users/wiselab/Videos/ARENA/20200819_ARENA Virtual Robot Arm.mp4
users/johnchoi/Videos/rays.mp4	users/wiselab/Videos/rays.mp4

users/johnchoi/BoschCar_Simplified/	users/wiselab/BoschCar_Simplified/
users/johnchoi/BoschPendulum/	users/wiselab/BoschPendulum/
users/johnchoi/Chess/	users/wiselab/Chess/
users/johnchoi/MyCobotPi/MyCobotPi_J0/MyCobotPi_J0.gltf	users/wiselab/MyCobotPi/MyCobotPi_J0/MyCobotPi_J0.gltf
users/johnchoi/MyCobotPi/MyCobotPi_J1/MyCobotPi_J1.gltf	users/wiselab/MyCobotPi/MyCobotPi_J1/MyCobotPi_J1.gltf
users/johnchoi/MyCobotPi/MyCobotPi_J2/MyCobotPi_J2.gltf	users/wiselab/MyCobotPi/MyCobotPi_J2/MyCobotPi_J2.gltf
users/johnchoi/MyCobotPi/MyCobotPi_J3/MyCobotPi_J3.gltf	users/wiselab/MyCobotPi/MyCobotPi_J3/MyCobotPi_J3.gltf
users/johnchoi/MyCobotPi/MyCobotPi_J4/MyCobotPi_J4.gltf	users/wiselab/MyCobotPi/MyCobotPi_J4/MyCobotPi_J4.gltf
users/johnchoi/MyCobotPi/MyCobotPi_J5/MyCobotPi_J5.gltf	users/wiselab/MyCobotPi/MyCobotPi_J5/MyCobotPi_J5.gltf
users/johnchoi/MyCobotPi/MyCobotPi_J6/MyCobotPi_J6.gltf	users/wiselab/MyCobotPi/MyCobotPi_J6/MyCobotPi_J6.gltf

users/agr/scans/mill19_2M_8K_v2.glb	users/wiselab/scans/mill19_2M_8K_v2.glb
users/ececapstone/ballbot_sm/ballbot.glb	users/wiselab/ballbot_sm/ballbot.glb

users/conixadmin/posters/ltvideo.png	users/wiselab/posters/ltvideo.png
users/conixadmin/posters/lvideo.png	users/wiselab/posters/lvideo.png
users/conixadmin/posters/poster_imgs/	users/wiselab/posters/poster_imgs/
users/conixadmin/posters/poster_pdfs/	users/wiselab/posters/poster_pdfs/
users/conixadmin/posters/ppdf.png	users/wiselab/posters/ppdf.png
EOF

if (( missing > 0 )); then
    echo "Completed with $missing missing source item(s)."
    exit 1
else
    echo "All items copied successfully."
fi
