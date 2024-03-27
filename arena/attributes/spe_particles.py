from .attribute import Attribute


class SpeParticles(Attribute):
    """
    SpeParticles attribute class to manage its properties in the ARENA: GPU based particle systems in A-Frame. More properties at <https://github.com/harlyq/aframe-spe-particles-component> A-Frame SPE Particles component.
    Usage: `spe_particles=SpeParticles(...)`

    :param dict acceleration: For sphere and disc distributions, only the x axis is used. Defaults to '{'x': 0, 'y': 0, 'z': 0}' (optional)
    :param str accelerationDistribution: Distribution of particle acceleration, for disc and sphere, only the x component will be used. if set to NONE use the 'distribution' attribute for accelerationDistribution. Allows [none, box, sphere, disc] Defaults to 'none' (optional)
    :param dict accelerationSpread: Spread of the particle's acceleration. for sphere and disc distributions, only the x axis is used. Defaults to '{'x': 0, 'y': 0, 'z': 0}' (optional)
    :param float activeMultiplier: Multiply the rate of particles emission, if larger than 1 then the particles will be emitted in bursts. note, very large numbers will emit all particles at once. Defaults to '1' (optional)
    :param bool affectedByFog: If true, the particles are affected by THREE js fog. Defaults to 'True' (optional)
    :param float alphaTest: Alpha values below the alphaTest threshold are considered invisible. Defaults to '0' (optional)
    :param list[float] angle: 2D rotation of the particle over the particle's lifetime, max 4 elements. Defaults to '[0]' (optional)
    :param list[float] angleSpread: Spread in angle over the particle's lifetime, max 4 elements. Defaults to '[0]' (optional)
    :param str blending: Blending mode, when drawing particles. Allows [no, normal, additive, subtractive, multiply, custom] Defaults to 'normal' (optional)
    :param list[str] color: Array of colors over the particle's lifetime, max 4 elements. Defaults to '['#fff']' (optional)
    :param list[dict] colorSpread: Spread to apply to colors, spread an array of vec3 (r g b) with 0 for no spread. note the spread will be re-applied through-out the lifetime of the particle. (optional)
    :param bool depthTest: If true, don't render a particle's pixels if something is closer in the depth buffer. Defaults to 'True' (optional)
    :param bool depthWrite: If true, particles write their depth into the depth buffer. this should be false if we use transparent particles. (optional)
    :param str direction: Make the emitter operate forward or backward in time. Allows [forward, backward] Defaults to 'forward' (optional)
    :param str distribution: Distribution for particle positions, velocities and acceleration. will be overridden by specific '...Distribution' attributes. Allows [box, sphere, disc] Defaults to 'box' (optional)
    :param float drag: Apply resistance to moving the particle, 0 is no resistance, 1 is full resistance, particle will stop moving at half of it's maxAge. Defaults to '0' (optional)
    :param float dragSpread: Spread to apply to the drag attribute. Defaults to '0' (optional)
    :param float duration: Duration of the emitter (seconds), if less than 0 then continuously emit particles. Defaults to '-1' (optional)
    :param float emitterScale: Global scaling factor for all particles from the emitter. Defaults to '100' (optional)
    :param bool enableInEditor: Enable the emitter while the editor is active (i.e. while scene is paused). (optional)
    :param bool enabled: Enable/disable the emitter. Defaults to 'True' (optional)
    :param bool frustumCulled: Enable/disable frustum culling. (optional)
    :param bool hasPerspective: If true, particles will be larger the closer they are to the camera. Defaults to 'True' (optional)
    :param float maxAge: Maximum age of a particle before reusing. Defaults to '1' (optional)
    :param float maxAgeSpread: Variance for the 'maxAge' attribute. Defaults to '0' (optional)
    :param list[float] opacity: Opacity over the particle's lifetime, max 4 elements. Defaults to '[1]' (optional)
    :param list[float] opacitySpread: Spread in opacity over the particle's lifetime, max 4 elements. Defaults to '[0]' (optional)
    :param int particleCount: Maximum number of particles for this emitter. Defaults to '100' (optional)
    :param str positionDistribution: Distribution of particle positions, disc and sphere will use the radius attributes. For box particles emit at 0,0,0, for sphere they emit on the surface of the sphere and for disc on the edge of a 2D disc on the XY plane. Allows [none, box, sphere, disc] Defaults to 'none' (optional)
    :param dict positionOffset: Fixed offset to the apply to the emitter relative to its parent entity. Defaults to '{'x': 0, 'y': 0, 'z': 0}' (optional)
    :param dict positionSpread: Particles are positioned within +- of these local bounds. for sphere and disc distributions only the x axis is used. Defaults to '{'x': 0, 'y': 0, 'z': 0}' (optional)
    :param float radius: Radius of the disc or sphere emitter (ignored for box). note radius of 0 will prevent velocity and acceleration if they use a sphere or disc distribution. Defaults to '1' (optional)
    :param dict radiusScale: Scales the emitter for sphere and disc shapes to form oblongs and ellipses. Defaults to '{'x': 1, 'y': 1, 'z': 1}' (optional)
    :param bool randomizeAcceleration: If true, re-randomize acceleration when re-spawning a particle, can incur a performance hit. (optional)
    :param bool randomizeAngle: If true, re-randomize angle when re-spawning a particle, can incur a performance hit. (optional)
    :param bool randomizeColor: If true, re-randomize colour when re-spawning a particle, can incur a performance hit. (optional)
    :param bool randomizeDrag: If true, re-randomize drag when re-spawning a particle, can incur a performance hit. (optional)
    :param bool randomizeOpacity: If true, re-randomize opacity when re-spawning a particle, can incur a performance hit. (optional)
    :param bool randomizePosition: If true, re-randomize position when re-spawning a particle, can incur a performance hit. (optional)
    :param bool randomizeRotation: If true, re-randomize rotation when re-spawning a particle, can incur a performance hit. (optional)
    :param bool randomizeSize: If true, re-randomize size when re-spawning a particle, can incur a performance hit. (optional)
    :param bool randomizeVelocity: If true, re-randomize velocity when re-spawning a particle, can incur a performance hit. (optional)
    :param str relative: World relative particles move relative to the world, while local particles move relative to the emitter (i.e. if the emitter moves, all particles move with it). Allows [local, world] Defaults to 'local' (optional)
    :param float rotation: Rotation in degrees. Defaults to '0' (optional)
    :param dict rotationAxis: Local axis when using rotation. Defaults to '{'x': 0, 'y': 0, 'z': 0}' (optional)
    :param dict rotationAxisSpread: Variance in the axis of rotation. Defaults to '{'x': 0, 'y': 0, 'z': 0}' (optional)
    :param float rotationSpread: Rotation variance in degrees. Defaults to '0' (optional)
    :param bool rotationStatic: If true, the particles are fixed at their initial rotation value. if false, the particle will rotate from 0 to the 'rotation' value. (optional)
    :param list[float] size: Array of sizes over the particle's lifetime, max 4 elements. Defaults to '[1]' (optional)
    :param list[float] sizeSpread: Spread in size over the particle's lifetime, max 4 elements. Defaults to '[0]' (optional)
    :param str texture: Texture to be used for each particle, may be a spritesheet. Examples: [blob.png, fog.png, square.png, explosion_sheet.png, fireworks_sheet.png], like path 'static/images/textures/blob.png'. (optional)
    :param int textureFrameCount: Number of frames in the spritesheet, negative numbers default to textureFrames.x * textureFrames.y. Defaults to '-1' (optional)
    :param int textureFrameLoop: Number of times the spritesheet should be looped over the lifetime of a particle. Defaults to '1' (optional)
    :param dict textureFrames: X and Y frames for a spritesheet. each particle will transition through every frame of the spritesheet over its lifetime (see textureFramesLoop). Defaults to '{'x': 1, 'y': 1}' (optional)
    :param bool useTransparency: Should the particles be rendered with transparency? Defaults to 'True' (optional)
    :param dict velocity: For sphere and disc distributions, only the x axis is used. Defaults to '{'x': 0, 'y': 0, 'z': 0}' (optional)
    :param str velocityDistribution: Distribution of particle velocities, for disc and sphere, only the x component will be used. if set to NONE use the 'distribution' attribute for velocityDistribution. Allows [none, box, sphere, disc] Defaults to 'none' (optional)
    :param dict velocitySpread: Variance for the velocity. Defaults to '{'x': 0, 'y': 0, 'z': 0}' (optional)
    :param float wiggle: Extra distance the particle moves over its lifetime. Defaults to '0' (optional)
    :param float wiggleSpread: +- spread for the wiggle attribute. Defaults to '0' (optional)
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Particles(SpeParticles):
    """
    Alternate name for SpeParticles.
    Usage: `spe_particles=Particles(...)`
    """
