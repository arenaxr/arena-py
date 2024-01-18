from .attribute import Attribute


class ParticleSystem(Attribute):
    """
    ParticleSystem attribute class to manage its properties in the ARENA: Particle system component for A-Frame.  More properties at (https://github.com/c-frame/aframe-particle-system-component) C-Frame Particle System component.
    Usage: particle_system=ParticleSystem(...)
    
    :param str preset: Preset configuration. [default, dust, snow, rain]; defaults to 'default' (optional)
    :param float maxAge: The particle's maximum age in seconds.; defaults to '6' (optional)
    :param dict positionSpread: Describes this emitter's position variance on a per-particle basis.; defaults to '{'x': 0, 'y': 0, 'z': 0}' (optional)
    :param float type: The default distribution this emitter should use to control its particle's spawn position and force behaviour. Possible values are 1 (box), 2 (sphere), 3 (disc); defaults to '1' (optional)
    :param str rotationAxis: Describes this emitter's axis of rotation. Possible values are x, y and z. [x, y, z]; defaults to 'x' (optional)
    :param float rotationAngle: The angle of rotation, given in radians. Dust preset is 3.14. (optional)
    :param float rotationAngleSpread: The amount of variance in the angle of rotation per-particle, given in radians. (optional)
    :param dict accelerationValue: Describes this emitter's base acceleration.; defaults to '{'x': 0, 'y': -10, 'z': 0}' (optional)
    :param dict accelerationSpread: Describes this emitter's acceleration variance on a per-particle basis.; defaults to '{'x': 10, 'y': 0, 'z': 10}' (optional)
    :param dict velocityValue: Describes this emitter's base velocity.; defaults to '{'x': 0, 'y': 25, 'z': 0}' (optional)
    :param dict velocitySpread: Describes this emitter's acceleration variance on a per-particle basis.; defaults to '{'x': 10, 'y': 7.5, 'z': 10}' (optional)
    :param float dragValue: Number between 0 and 1 describing drag applied to all particles. (optional)
    :param float dragSpread: Number describing drag variance on a per-particle basis. (optional)
    :param bool dragRandomise: WHen a particle is re-spawned, whether it's drag should be re-randomised or not. Can incur a performance hit. (optional)
    :param list color: Describes a particle's color. This property is a 'value-over-lifetime' property, meaning an array of values can be given to describe specific value changes over a particle's lifetime.; defaults to '['#0000FF', '#FF0000']' (optional)
    :param list size: Describes a particle's size.; defaults to '[1]' (optional)
    :param list sizeSpread: ; defaults to '[0]' (optional)
    :param float direction: The direction of the emitter. If value is 1, emitter will start at beginning of particle's lifecycle. If value is -1, emitter will start at end of particle's lifecycle and work it's way backwards.; defaults to '1' (optional)
    :param float duration: The duration in seconds that this emitter should live for. If not specified, the emitter will emit particles indefinitely. (optional)
    :param bool enabled: When true the emitter will emit particles, when false it will not. This value can be changed dynamically during a scene. While particles are emitting, they will disappear immediately when set to false.; defaults to 'True' (optional)
    :param float particleCount: The total number of particles this emitter will hold. NOTE: this is not the number of particles emitted in a second, or anything like that. The number of particles emitted per-second is calculated by particleCount ; defaults to '1000' (optional)
    :param str texture: The texture used by this emitter. Examples: [star2.png, smokeparticle.png, raindrop.png], like path 'static/images/textures/star2.png'; defaults to 'static/images/textures/star2.png' (optional)
    :param bool randomise: When a particle is re-spawned, whether it's position should be re-randomised or not. Can incur a performance hit. (optional)
    :param list opacity: Either a single number to describe the opacity of a particle.; defaults to '[1]' (optional)
    :param list opacitySpread: ; defaults to '[1]' (optional)
    :param str blending: The blending mode of the particles. Possible values are 0 (no blending), 1 (normal), 2 (additive), 3 (subtractive), 4 (multiply) [0, 1, 2, 3, 4]; defaults to '2' (optional)
    :param float maxParticleCount: ; defaults to '250000' (optional)
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
