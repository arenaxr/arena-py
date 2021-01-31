# Objects in ARENA-py

Objects are the main interface for placing content into the ARENA.

See https://arena.conix.io/content/messaging/examples.html.

# Creating an Object
See Appendix for all types of objects.

Attributes can be added upon Object creation in the three ways used below (special attributes like position, rotation, scale, color, etc. can be added with tuples, lists, or dictionaries).
```python
box = Box(
    object_id="my_box",
    position=Position(0,4,-2),
    rotation=(0,0,0,1),
    scale={"x":2,"y":2,"z":2}
)

arena.add_object(box)
```

# Adding Attributes
```python
# use update_attributes with kwargs to add attributes
box.update_attributes(physics=Physics(type="dynamic"))

# don't forget to call arena.update_object to see your chnages in the ARENA!
arena.update_object(box)
```

# Updating Attributes
Most attributes (except object_id, persist, ttl, and parent) are under the "data" field. Access these by using ```obj.data```.
```python
box.data.position.x = 2
# box.update_attributes(position=Position(2,4,-2)) works too
arena.update_object(box)
```

## Removing Object Attributes
```python
obj.data.click_listener = None
# obj.update_attributes(click_listener=None) works too
```

## Update Handler
The update_handler will be called whenever the object is updated by the library of by some external program
```python
def update(obj):
    print(obj)

obj.update_handler = update
# obj.update_attributes(update_handler=update) works too
```

# Appendix

## Box
```python
Box(...)
```

## Sphere
```python
Sphere(...)
```

## Circle
```python
Circle(...)
```

## Cone
```python
Cone(...)
```

## Cylinder
```python
Cylinder(...)
```

## Dodecahedron
```python
Dodecahedron(...)
```

## Icosahedron
```python
Icosahedron(...)
```

## Tetrahedron
```python
Tetrahedron(...)
```

## Octahedron
```python
Octahedron(...)
```

## Plane
```python
Plane(...)
```

## Ring
```python
Ring(...)
```

## Torus
```python
Torus(...)
```

## Triangle
```python
Triangle(...)
```

## GLTF
```python
GLTF(url, ...)
```

## Image
```python
Image(url, ...)
```

## Particle
```python
Particle(...)
```

## Text
```python
Text(...)
```

## Light
```python
Light(...)
```

## Line
```python
Line(start, end, ...)
```

## ThickLine
```python
ThickLine(path, lineWidth, ...)
```

## Camera
```python
Camera(object_id, ...)
```

## Generic Object
For objects that might not exist yet. Inherit from this class to create custom objects.
```python
Object(object_type, ...)
```

## ARENA Object JSON example
```json
{
    "object_id": "my_box",
    "type": "object",
    "persist": false,
    "data": {
        "object_type": "box",
        "position": {
            "x": 0,
            "y": 4,
            "z": -2
        },
        "scale": {
            "x": 2,
            "y": 2,
            "z": 2
        },
        # more attributes here
    },
    "timestamp" : "[time goes here]"
}
```
