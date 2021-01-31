# Attributes in ARENA-py

Attributes are used to specify parameters for ARENA Objects.

See https://arena.conix.io/content/messaging/examples.html.

## Accessing Object Attributes
Usually, attributes (except for object_id, persist, ttl, and parent) are under the data field:
```python
obj.object_id
obj.persist
...
obj.data.position
obj.data.rotation
...
obj.data.material
# etc etc
```

# Appendix
## Position
The position of an object can be specified by:
```python
position=Position(x, y, z)
# or
position=(x, y, z)
```

## Rotation
The rotation (in quaternions) of an object can be specified by:
```python
rotation=Rotation(x, y, z, w)
# or
rotation=(x, y, z, w)
```
The rotation (in euler coordinates) of an object can be specified by:
```python
rotation=Rotation(x, y, z)
# or
rotation=(x, y, z)
```
Note: All units for rotation are in **radians**.

## Scale
The scale of an object can be specified by:
```python
scale=Scale(x, z, y)
# or
scale=(x, y, z)
```

## Color
The color of an object can be specified by:
```python
color=Color(red, green, blue)
# or
color=(red, green, blue)
```

## Animation
An animation can be added by:
```python
animation=Animation(...) or animation_mixer=Animation(...) for GLTF animations
```
Note: please use "start" and "end" as arguments for fields "from" and "to" in json (done to prevent using the python reserved word "from"):
```python
Animation(start="something", end="something else ") == Animation(to="something", from="something else ")
```

## Sound
A sound can be added to an object using:
```python
sound=Sound(positional, poolSize, autoplay, src, ...)
```

## Material
The transparency of an object can be set by:
```python
material=Material(transparent, opacity, ...)
```

## GotoUrl
Goes to a url on click. Note: click-listener must be True for this to work:
```python
goto_url=GotoUrl(dest, on, url)
```

## Impulse
An impulse can be added by:
```python
impulse=Impulse(on, force, position)
```

## Physics
Physics ("none", "static", or "dynamic") can be added with:
```python
physics=Physics(type)
```
or
```python
dynamic_body=Physics(type)
```

## Generic attribute
For attributes that are not specified by the library, you can use this (put anything you want in the "...")! Inherit from this class to create custom attributes.
```python
Attribute(...)
```

## Additional Attributes (which are just specified as numbers or strings) may include:
```python
persist=True
ttl=30  # seconds
clickable=True
# click_listener=True works too
# etc.
# see https://arena.conix.io/content/messaging/examples.html
```
