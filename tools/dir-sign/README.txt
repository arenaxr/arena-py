This program creates 3D directories with clickable links.

You configure it with environmental variables like this:
export MQTTH=arena.andrew.cmu.edu
export REALM=realm
export SCENE=myScene
export JSONCFG=directory_cfg.json

Then run it:
python3 dir-sign.py

See some example configuration files in the "configs" directory. Options defining the visual aspects of the sign (color, font, etc) are defined at the top of the python program.  Will add them to the json config someday...
