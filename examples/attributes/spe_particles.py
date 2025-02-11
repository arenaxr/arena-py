"""Particles

Particles are based on [aframe-spe-particles-component](https://github.com/harlyq/aframe-spe-particles-component), javascript loaded from [aframe-spe-particles-component.min.js](https://unpkg.com/aframe-spe-particles-component@^1.0.4/dist/aframe-spe-particles-component.min.js).

For now, it's not directly supported, but rather by passing JSON inside the `data{}` element. The syntax for parameter names has been updated so instead of a name like this that is `space-separated` it becomes `spaceSeparated` (camel case). Three examples here have been created starting with the examples in [aframe-spe-particles-component examples](https://harlyq.github.io/aframe-spe-particles-component/) then reformulating to ARENA JSON syntax.

{
  "object_id": "smoke",
  "action": "create",
  "type": "object",
  "data": {
    "object_type": "entity",
    "position": { "x": 0, "y": 1, "z": -3.9 },
    "rotation": { "x": 0, "y": 0, "z": 0, "w": 1 },
    "scale": { "x": 0.01, "y": 0.01, "z": 0.01 },
    "spe-particles": {
      "texture": "static/images/textures/fog.png",
      "velocity": "1 30 0",
      "velocitySpread": "2 1 0.2",
      "particleCount": 50,
      "maxAge": 4,
      "size": "3, 8",
      "opacity": "0, 1, 0",
      "color": "#aaa, #222"
    }
  }
}

Particles are very complicated and take a lot of parameters. It would not make sense to translate all of them into explicit ARENA types, thus this flexible 'raw JSON' format is used.
"""

from arena import *

scene = Scene(host="arenaxr.org", scene="example")

position = Position(0, 0, -3)


@scene.run_once
def make_fire():
    sparks = Object(
        object_id="sparks",
        position=position,
        spe_particles=Particles(
            texture="static/images/textures/square.png",
            color=["yellow", "red"],
            particleCount=10,
            maxAge=0.5,
            maxAgeSpread=0.4,
            velocity=Position(0, 5, 0),
            velocitySpread=Position(0, 3, 0),
            wiggle=1,
            wiggleSpread=5,
            emitterScale=50,
            sizeSpread=[0.5],
            randomizeVelocity=True,
        )
    )
    scene.add_object(sparks)

    smoke = Object(
        object_id="smoke",
        position=position,
        spe_particles=Particles(
            texture="static/images/textures/fog.png",
            velocity=Position(0.4, 2, 0),
            velocitySpread=Position(1.4, 0, 1.4),
            particleCount=50,
            maxAge=4,
            size=[8, 16],
            opacity=[0, 1, 0],
            color=["#666", "#222"],
        )
    )
    scene.add_object(smoke)

    flames = Object(
        object_id="flames",
        position=position,
        spe_particles=Particles(
            texture="static/images/textures/explosion_sheet.png",
            textureFrames={"x": 5, "y": 5},
            velocity=Position(0.4, 0.1, 0),
            acceleration=Position(0, 2, 0),
            accelerationSpread=Position(0, 2, 0),
            velocitySpread=Position(0.4, 0, 0.4),
            particleCount=15,
            maxAge=1,
            size=[4, 8],
            sizeSpread=[2],
            opacity=[1, 0],
            wiggle=0,
            blending="additive",
        )
    )
    scene.add_object(flames)


scene.run_tasks()
