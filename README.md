# ARENA Py - Python Examples
Draw objects in the ARENA using python.

Install required packages:
```
pip install -r requirements.txt
```

Hello ARENA

```
cd examples
python hello.py
```
(view results at https://xr.andrew.cmu.edu?scene=hello) 

hello.py
```
import arena
arena.init("oz.andrew.cmu.edu", "realm", "hello")
arena.Object(arena.Shape.cube)
arena.handle_events()
```
