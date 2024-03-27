from .attribute import Attribute

class Material(Attribute):
    """
    Material attribute class to manage its properties in the ARENA: The material properties of the object's surface. More properties at <https://aframe.io/docs/1.5.0/components/material.html> A-Frame Material.
    Usage: `material=Material(...)`

    :param float alphaTest: Alpha test threshold for transparency. (optional)
    :param float anisotropy: The anisotropic filtering sample rate to use for the textures. A value of 0 means the default value will be used, see renderer. (optional)
    :param str blending: The blending mode for the material's RGB and Alpha sent to the WebGLRenderer. Allows [none, normal, additive, subtractive, multiply] Defaults to 'normal' (optional)
    :param str color: Base diffuse color. Defaults to '#ffffff' (optional)
    :param str combine: How the environment map mixes with the material. Requires shader: phong. Allows [mix, add, multiply] Defaults to 'mix' (optional)
    :param bool depthTest: Whether depth testing is enabled when rendering the material. Defaults to 'True' (optional)
    :param bool depthWrite: Render when depth test succeeds. Defaults to 'True' (optional)
    :param bool dithering: Whether material is dithered with noise. Removes banding from gradients like ones produced by lighting. Defaults to 'True' (optional)
    :param str emissive: The color of the emissive lighting component. Used to make objects produce light even without other lighting in the scene. Requires shader: standard or phong Defaults to '#000000' (optional)
    :param float emissiveIntensity: Intensity of the emissive lighting component. Requires shader: standard or phong Defaults to '1' (optional)
    :param bool flatShading: Use THREE.FlatShading rather than THREE.StandardShading. (optional)
    :param bool fog: Whether or not material is affected by fog. Defaults to 'True' (optional)
    :param int height: Height of video (in pixels), if defining a video texture. Requires shader: standard or flat. Defaults to '256' (optional)
    :param float metalness: How metallic the material is from 0 to 1. Requires shader: standard. (optional)
    :param bool npot: Use settings for non-power-of-two (NPOT) texture. (optional)
    :param dict offset: Texture offset to be used. Defaults to '{'x': 0, 'y': 0}' (optional)
    :param float opacity: Extent of transparency. If the transparent property is not true, then the material will remain opaque and opacity will only affect color. Defaults to '1' (optional)
    :param float reflectivity: How much the environment map affects the surface. Requires shader: phong. Defaults to '0.9' (optional)
    :param bool refract: Whether the defined envMap should refract. Requires shader: phong. (optional)
    :param float refractionRatio: 1/refractive index of the material. Requires shader: phong. Defaults to '0.98' (optional)
    :param dict repeat: How many times a texture (defined by src) repeats in the X and Y direction. Defaults to '{'x': 1, 'y': 1}' (optional)
    :param float roughness: How rough the material is from 0 to 1. A rougher material will scatter reflected light in more directions than a smooth material. Requires shader: standard. (optional)
    :param str shader: Which material to use. Defaults to the standard material. Can be set to the flat material or to a registered custom shader material. Allows [flat, standard, phong] Defaults to 'standard' (optional)
    :param float shininess: How shiny the specular highlight is; a higher value gives a sharper highlight. Requires shader: phong. Defaults to '30' (optional)
    :param str side: Which sides of the mesh to render. Allows [front, back, double] Defaults to 'front' (optional)
    :param str specular: This defines how shiny the material is and the color of its shine. Requires shader: phong. Defaults to '#111111' (optional)
    :param str src: URI, relative or full path of an image/video file. e.g. 'store/users/wiselab/images/360falls.mp4'. (optional)
    :param bool toneMapped: Whether to ignore toneMapping, set to false you are using renderer.toneMapping and an element should appear to emit light. Requires shader: flat. Defaults to 'True' (optional)
    :param bool transparent: Whether material is transparent. Transparent entities are rendered after non-transparent entities. (optional)
    :param bool vertexColorsEnabled: Whether to use vertex or face colors to shade the material. (optional)
    :param bool visible: Whether material is visible. Raycasters will ignore invisible materials. Defaults to 'True' (optional)
    :param int width: Width of video (in pixels), if defining a video texture. Requires shader: standard or flat. Defaults to '512' (optional)
    :param bool wireframe: Whether to render just the geometry edges. (optional)
    :param int wireframeLinewidth: Width in px of the rendered line. Defaults to '2' (optional)
    """
    def __init__(self, **kwargs):
        if "opacity" in kwargs:
            # kwargs["transparent"] = True # need to be transparent to be opaque
            if kwargs["opacity"] > 1.0: # keep opacity between 0.0 and 1.0
                kwargs["opacity"] = float(kwargs["opacity"]) / 100
            kwargs["opacity"] = max(0.0, kwargs["opacity"])
            kwargs["opacity"] = min(kwargs["opacity"], 1.0)

        super().__init__(**kwargs)
