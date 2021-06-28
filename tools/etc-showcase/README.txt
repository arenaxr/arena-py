'etc-room.py' does the following:
	1) creates a shareable screen called "etc-share"
	2) Adds laser pointer click functionality to any "clickable" (Click Listener=True)  object
	3) Spins the sign when the button is selected
	4) Create a zero sized object called "screenshare" that is far away

To run, do the following in the shell:

> export NAMESPACE=etc
> export SCENE=01_Activate
> python3 etc-room.py
...


You can also run the 'pinata.py' demo with:

> export NAMESPACE=etc
> export SCENE=ProjectHub
> python3 pinata.py

-----

edit-rooms.sh: goes throughout the scenes listed in project-rooms.txt and adjusts settings
