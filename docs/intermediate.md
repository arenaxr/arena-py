# Intermediate Example - Exploring more functionality!

## Updating object attributes
```python
box = Box(object_id="my_box", position=Position(0,4,-2), scale=Scale(2,2,2))
scene.add_object(box)

box.update_attributes(position=Position(2,4,-2))
scene.update_object(box)
```

## Parent-Child
We can define child objects whose position will be relative to its parent object:
```python
text = Text(object_id="my_text", text="Welcome to arena-py!" position=Position(0,2,0), parent=box)
scene.add_object(text)
```

## Decorators for tasks and periodic tasks
Instead of doing
```python
def main():
    # your code here

scene.run_once(main)
```
You can instead do
```python
@scene.run_once
def main():
    # your code here
```

Lets define a periodic task that runs every 500 milliseconds:
```python
x = 0
@scene.run_forever(interval_ms=500)
def periodic():
    global x    # non allocated variables need to be global
    box.update_attributes(position=Position(x,3,0))
    scene.update_object(box)
    x += 0.1
```

## Run tasks
```python
# note that we do not have to do scene.run_once or scene.run_forever
scene.run_tasks()
```

Now, go into the scene to see your box move with text!

# Appendix
```python
from arena import *

# setup library
scene = Scene(host="arenaxr.org", realm="realm", scene="example")

# make a box
box = Box(object_id="my_box", position=Position(0,4,-2), scale=Scale(2,2,2))

@scene.run_once
def main():
    # add the box
    scene.add_object(box)

    # add text
    text = Text(object_id="my_text", text="Welcome to arena-py!", position=Position(0,2,0), parent=box)
    scene.add_object(text)

x = 0
@scene.run_forever(interval_ms=500)
def periodic():
    global x    # non allocated variables need to be global
    box.update_attributes(position=Position(x,3,0))
    scene.update_object(box)
    x += 0.1

# start tasks
scene.run_tasks()
```
