"""Persisted Objects

If we want our objects to return to the scene when we next open or reload our browser, we can commit them on creation to the ARENA Persistence DB by setting `"persist": true`.

{
  "object_id": "Ball2",
  "action": "create",
  "persist": true,
  "data": {
    "position": { "x": -1, "y": 1, "z": -1 },
    "material": { "color": "blue" },
    "object_type": "sphere"
  }
}
"""
