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
