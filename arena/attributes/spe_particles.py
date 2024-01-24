from .attribute import Attribute

class SpeParticles(Attribute):
    """
    SpeParticles attribute class to manage its properties in the ARENA: GPU based particle systems in A-Frame.  More properties at (https://github.com/harlyq/aframe-spe-particles-component) A-Frame SPE Particles component.
    Usage: spe_particles=SpeParticles(...)

    :param dict acceleration: for sphere and disc distributions, only the x axis is used; defaults to '{'x': 0, 'y': 0, 'z': 0}' (optional)
    :param str accelerationDistribution: distribution of particle acceleration, for disc and sphere, only the x component will be used. if set to NONE use the 'distribution' attribute for accelerationDistribution [none, box, sphere, disc]; defaults to 'none' (optional)
    :param dict accelerationSpread: spread of the particle's acceleration. for sphere and disc distributions, only the x axis is used; defaults to '{'x': 0, 'y': 0, 'z': 0}' (optional)
    :param float activeMultiplier: multiply the rate of particles emission, if larger than 1 then the particles will be emitted in bursts. note, very large numbers will emit all particles at once; defaults to '1' (optional)
    :param bool affectedByFog: if true, the particles are affected by THREE js fog; defaults to 'True' (optional)
    :param float alphaTest: alpha values below the alphaTest threshold are considered invisible; defaults to '0' (optional)
    :param list[float] angle: 2D rotation of the particle over the particle's lifetime, max 4 elements; defaults to '[0]' (optional)
    :param list[float] angleSpread: spread in angle over the particle's lifetime, max 4 elements; defaults to '[0]' (optional)
    :param str blending: blending mode, when drawing particles [no, normal, additive, subtractive, multiply, custom]; defaults to 'normal' (optional)
    :param list[str] color: array of colors over the particle's lifetime, max 4 elements; defaults to '['#fff']' (optional)
    :param list[dict] colorSpread: spread to apply to colors, spread an array of vec3 (r g b) with 0 for no spread. note the spread will be re-applied through-out the lifetime of the particle (optional)
    :param bool depthTest: if true, don't render a particle's pixels if something is closer in the depth buffer; defaults to 'True' (optional)
    :param bool depthWrite: if true, particles write their depth into the depth buffer. this should be false if we use transparent particles (optional)
    :param str direction: make the emitter operate forward or backward in time [forward, backward]; defaults to 'forward' (optional)
    :param str distribution: distribution for particle positions, velocities and acceleration. will be overridden by specific '...Distribution' attributes [box, sphere, disc]; defaults to 'box' (optional)
    :param float drag: apply resistance to moving the particle, 0 is no resistance, 1 is full resistance, particle will stop moving at half of it's maxAge; defaults to '0' (optional)
    :param float dragSpread: spread to apply to the drag attribute; defaults to '0' (optional)
    :param float duration: duration of the emitter (seconds), if less than 0 then continuously emit particles; defaults to '-1' (optional)
    :param float emitterScale: global scaling factor for all particles from the emitter; defaults to '100' (optional)
    :param bool enableInEditor: enable the emitter while the editor is active (i.e. while scene is paused) (optional)
    :param bool enabled: enable/disable the emitter; defaults to 'True' (optional)
    :param bool frustumCulled: enable/disable frustum culling (optional)
    :param bool hasPerspective: if true, particles will be larger the closer they are to the camera; defaults to 'True' (optional)
    :param float maxAge: maximum age of a particle before reusing; defaults to '1' (optional)
    :param float maxAgeSpread: variance for the 'maxAge' attribute; defaults to '0' (optional)
    :param list[float] opacity: opacity over the particle's lifetime, max 4 elements; defaults to '[1]' (optional)
    :param list[float] opacitySpread: spread in opacity over the particle's lifetime, max 4 elements; defaults to '[0]' (optional)
    :param int particleCount: maximum number of particles for this emitter; defaults to '100' (optional)
    :param str positionDistribution: distribution of particle positions, disc and sphere will use the radius attributes. For box particles emit at 0,0,0, for sphere they emit on the surface of the sphere and for disc on the edge of a 2D disc on the XY plane [none, box, sphere, disc]; defaults to 'none' (optional)
    :param dict positionOffset: fixed offset to the apply to the emitter relative to its parent entity; defaults to '{'x': 0, 'y': 0, 'z': 0}' (optional)
    :param dict positionSpread: particles are positioned within +- of these local bounds. for sphere and disc distributions only the x axis is used; defaults to '{'x': 0, 'y': 0, 'z': 0}' (optional)
    :param float radius: radius of the disc or sphere emitter (ignored for box). note radius of 0 will prevent velocity and acceleration if they use a sphere or disc distribution; defaults to '1' (optional)
    :param dict radiusScale: scales the emitter for sphere and disc shapes to form oblongs and ellipses; defaults to '{'x': 1, 'y': 1, 'z': 1}' (optional)
    :param bool randomizeAcceleration: if true, re-randomize acceleration when re-spawning a particle, can incur a performance hit (optional)
    :param bool randomizeAngle: if true, re-randomize angle when re-spawning a particle, can incur a performance hit (optional)
    :param bool randomizeColor: if true, re-randomize colour when re-spawning a particle, can incur a performance hit (optional)
    :param bool randomizeDrag: if true, re-randomize drag when re-spawning a particle, can incur a performance hit (optional)
    :param bool randomizeOpacity: if true, re-randomize opacity when re-spawning a particle, can incur a performance hit (optional)
    :param bool randomizePosition: if true, re-randomize position when re-spawning a particle, can incur a performance hit (optional)
    :param bool randomizeRotation: if true, re-randomize rotation when re-spawning a particle, can incur a performance hit (optional)
    :param bool randomizeSize: if true, re-randomize size when re-spawning a particle, can incur a performance hit (optional)
    :param bool randomizeVelocity: if true, re-randomize velocity when re-spawning a particle, can incur a performance hit (optional)
    :param str relative: world relative particles move relative to the world, while local particles move relative to the emitter (i.e. if the emitter moves, all particles move with it) [local, world]; defaults to 'local' (optional)
    :param float rotation: rotation in degrees; defaults to '0' (optional)
    :param dict rotationAxis: local axis when using rotation; defaults to '{'x': 0, 'y': 0, 'z': 0}' (optional)
    :param dict rotationAxisSpread: variance in the axis of rotation; defaults to '{'x': 0, 'y': 0, 'z': 0}' (optional)
    :param float rotationSpread: rotation variance in degrees; defaults to '0' (optional)
    :param bool rotationStatic: if true, the particles are fixed at their initial rotation value. if false, the particle will rotate from 0 to the 'rotation' value (optional)
    :param list[float] size: array of sizes over the particle's lifetime, max 4 elements; defaults to '[1]' (optional)
    :param list[float] sizeSpread: spread in size over the particle's lifetime, max 4 elements; defaults to '[0]' (optional)
    :param str texture: texture to be used for each particle, may be a spritesheet.  Examples: [blob.png, fog.png, square.png, explosion_sheet.png, fireworks_sheet.png], like path 'static/images/textures/blob.png' (optional)
    :param int textureFrameCount: number of frames in the spritesheet, negative numbers default to textureFrames.x * textureFrames.y; defaults to '-1' (optional)
    :param int textureFrameLoop: number of times the spritesheet should be looped over the lifetime of a particle; defaults to '1' (optional)
    :param dict textureFrames: x and y frames for a spritesheet. each particle will transition through every frame of the spritesheet over its lifetime (see textureFramesLoop); defaults to '{'x': 1, 'y': 1}' (optional)
    :param bool useTransparency: should the particles be rendered with transparency?; defaults to 'True' (optional)
    :param dict velocity: for sphere and disc distributions, only the x axis is used; defaults to '{'x': 0, 'y': 0, 'z': 0}' (optional)
    :param str velocityDistribution: distribution of particle velocities, for disc and sphere, only the x component will be used. if set to NONE use the 'distribution' attribute for velocityDistribution [none, box, sphere, disc]; defaults to 'none' (optional)
    :param dict velocitySpread: variance for the velocity; defaults to '{'x': 0, 'y': 0, 'z': 0}' (optional)
    :param float wiggle: extra distance the particle moves over its lifetime; defaults to '0' (optional)
    :param float wiggleSpread: +- spread for the wiggle attribute; defaults to '0' (optional)
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Particles(SpeParticles):
    """
    Alternate name for SpeParticles.
    Usage: spe_particles=Particles(...)
    """
