#!/bin/bash

# NOTE: iterations of a while ** in a pipeline ** are executed inside a subshell
# see: http://mywiki.wooledge.org/BashFAQ/024
cat project-rooms.txt | while read room; do
  export NAMESPACE=etc
  export SCENE=$room
  python3 edit-room.py
done
