"""Attribute Instances

Test all instance types for Position, Rotation, and Scale attributes.
Exercises: scalar args, tuple, dict, and string (float) construction.
Validates fix for issues #208 and #224 (map(int,...) crash on float strings).
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")


@scene.run_once
def test_attribute_instances():
    # Position: scalar args
    p1 = Position(1.5, 2.0, -3.5)
    assert p1.x == 1.5 and p1.y == 2.0 and p1.z == -3.5

    # Position: tuple
    p2 = Position((1.5, 2.0, -3.5))
    assert p2.x == 1.5 and p2.y == 2.0 and p2.z == -3.5

    # Position: dict
    p3 = Position({"x": 1.5, "y": 2.0, "z": -3.5})
    assert p3.x == 1.5 and p3.y == 2.0 and p3.z == -3.5

    # Position: string (issue #224 crash case)
    p4 = Position("1.5 2.0 -3.5")
    assert p4.x == 1.5 and p4.y == 2.0 and p4.z == -3.5

    # Position: int string (backwards compat)
    p5 = Position("1 2 3")
    assert p5.x == 1.0 and p5.y == 2.0 and p5.z == 3.0

    print("Position: all instance types passed")

    # Rotation: scalar args (euler)
    r1 = Rotation(45.5, 90.0, 0.0)
    assert r1.x == 45.5 and r1.y == 90.0 and r1.z == 0.0

    # Rotation: tuple (euler)
    r2 = Rotation((45.5, 90.0, 0.0))
    assert r2.x == 45.5 and r2.y == 90.0 and r2.z == 0.0

    # Rotation: dict (quaternion)
    r3 = Rotation({"x": 0.0, "y": 0.7, "z": 0.0, "w": 0.7})
    assert r3.x == 0.0 and r3.y == 0.7 and r3.z == 0.0 and r3.w == 0.7

    # Rotation: string (issue #208 crash case)
    r4 = Rotation("45 90 0")
    assert r4.x == 45.0 and r4.y == 90.0 and r4.z == 0.0

    # Rotation: float string
    r5 = Rotation("45.5 90.0 0.0")
    assert r5.x == 45.5 and r5.y == 90.0 and r5.z == 0.0

    print("Rotation: all instance types passed")

    # Scale: scalar args
    s1 = Scale(1.5, 2.0, 0.5)
    assert s1.x == 1.5 and s1.y == 2.0 and s1.z == 0.5

    # Scale: tuple
    s2 = Scale((1.5, 2.0, 0.5))
    assert s2.x == 1.5 and s2.y == 2.0 and s2.z == 0.5

    # Scale: dict
    s3 = Scale({"x": 1.5, "y": 2.0, "z": 0.5})
    assert s3.x == 1.5 and s3.y == 2.0 and s3.z == 0.5

    # Scale: string (float)
    s4 = Scale("1.5 2.0 0.5")
    assert s4.x == 1.5 and s4.y == 2.0 and s4.z == 0.5

    # Scale: int string (backwards compat)
    s5 = Scale("1 2 3")
    assert s5.x == 1.0 and s5.y == 2.0 and s5.z == 3.0

    print("Scale: all instance types passed")

    # Visual confirmation: create objects using each instance type
    scene.add_object(Box(
        object_id="attr_test_scalar",
        position=Position(0, 2, -3),
        rotation=Rotation(0, 0, 0),
        scale=Scale(0.5, 0.5, 0.5),
        material=Material(color=Color(255, 0, 0)),
    ))
    scene.add_object(Box(
        object_id="attr_test_tuple",
        position=(1.5, 2, -3),
        rotation=(0, 45.0, 0),
        scale=(0.5, 0.5, 0.5),
        material=Material(color=Color(0, 255, 0)),
    ))
    scene.add_object(Box(
        object_id="attr_test_dict",
        position={"x": 3.0, "y": 2, "z": -3},
        rotation={"x": 0, "y": 0, "z": 0, "w": 1},
        scale={"x": 0.5, "y": 0.5, "z": 0.5},
        material=Material(color=Color(0, 0, 255)),
    ))

    print("All attribute instance tests passed!")


scene.run_tasks()
