#!/bin/bash

cat scene-list.txt | while read scene; do
  export NAMESPACE=$(echo $scene | cut -f 1 -d '/')
  export SCENE=$(echo $scene | cut -f 2 -d '/')
  #echo 'Scene:'$NAMESPACE'/'$SCENE
  python3 edit-room.py
done
