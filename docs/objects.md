# Objects in ARENA-py

Objects are the main interface for placing content into the ARENA.

## Cube
```python
Cube(...)
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
For objects that might not exist yet.
```python
Object(object_type, ...)
```

# Updating Object Attributes
```python
cube = Cube(object_id="my_cube", position=Position(0,4,-2), scale=Scale(2,2,2))
arena.add_object(cube)

cube.update_attributes(position=Position(2,4,-2))
arena.update_object(cube)
```

# ARENA Object JSON example
```json
{
    "object_id": "my_cube",
    "type": "object",
    "persist": false,
    "data": {
        "object_type": "cube",
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
    "action": "create",
    "timestamp" : "[time goes here]"
}
```
