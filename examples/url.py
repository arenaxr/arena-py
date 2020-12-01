# url.py
#
import arena
arena.init("arena.andrew.cmu.edu", "realm", "example")

print("Three clickable URL cubes targetted to different windows" )

popup = arena.Object(
                objType=arena.Shape.cube,
                location=( -3, 0, -5),
                color=(255,0,0),
                clickable=True,
                data='{"goto-url": { "dest":"popup", "on": "mousedown", "url": "http:www.conix.io"} } ',
) 

newtab = arena.Object(
                objType=arena.Shape.cube,
                location=( 0, 0, -5),
                color=(0,255,0),
                clickable=True,
                data='{"goto-url": { "dest":"newtab", "on": "mousedown", "url": "http:www.eet.com"} } ',
) 

default = arena.Object(
                objType=arena.Shape.cube,
                location=( 3, 0, -5),
                color=(0,0,255),
                clickable=True,
                data='{"goto-url": { "dest":"sametab", "on": "mousedown", "url": "http:www.formula1.com"} } ',
) 



arena.handle_events()
