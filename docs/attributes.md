# Attributes in ARENA-py

Attributes are used to specify parameters for ARENA Objects.

## Position
The position of an object can be specified by:
```python
position=Position(x, y, z)
```

## Rotation
The rotation (in quaternions) of an object can be specified by:
```python
rotation=Rotation(x, y, z, w)
```

## Scale
The scale of an object can be specified by:
```python
scale=Scale(x, z, y)
```

## AnimationMixer
An animation can be added by :
```python
animation=AnimationMixer(clip, loop, repetitions, timeScale)
```

## Sound
A sound can be added to an object using:
```python
sound=Sound(positional, poolSize, autoplay, src)
```

## Material
The transparency of an object can be set by:
```python
material=Material(transparent, opacity)
```

## GotoUrl
Goes to a url on click. Note: click-listener must be True for this to work:
```python
goto_url=GotoUrl(dest, on, url)
```

## Impulse (note: does not work!)
An impulse can be added by:
```python
impulse=Impulse(on, force, position)
```

## Physics (note: does not work!)
Physics ("none", "static", or "dynamic") can be added with:
```python
physics=Physics(type)
```
or
```python
dynamic_body=Physics(type)
```

## Generic attribute
For attributes that are not specified by the library, you can use this (put anything you want in the "...")!:
```python
Attribute(...)
```

## Getting attributes
Usually, attributes are under data
```python
obj.data.position
obj.data.rotation
# ...
obj.data.material
# etc etc
```
