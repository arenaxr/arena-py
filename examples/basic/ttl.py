"""Temporary Objects: TTL

It's desirable to have objects that don't last forever and pile up. For that there is the 'ttl' parameter that gives objects a lifetime, in seconds. This is an example usage for a sphere that disappears after 5 seconds.

{
  "object_id": "Ball2",
  "action": "create",
  "ttl": 5,
  "data": {
    "position": { "x": -1, "y": 1, "z": -1 },
    "material": { "color": "blue" },
    "object_type": "sphere"
  }
}
"""
