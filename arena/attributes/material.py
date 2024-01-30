from .attribute import Attribute

class Material(Attribute):
    """
    Material attribute class to manage its properties in the ARENA: The material properties of the object's surface.  More properties at (https://aframe.io/docs/1.5.0/components/material.html) A-Frame Material.
    Usage: material=Material(...)
    
    :param float alphaTest: Alpha test threshold for transparency. (optional)
    :param str blending: The blending mode for the material's RGB and Alpha sent to the WebGLRenderer. Allows [none, normal, additive, subtractive, multiply] Defaults to 'normal' (optional)
    :param str color: Base diffuse color. Defaults to '#7f7f7f' (optional)
    :param bool depthTest: Whether depth testing is enabled when rendering the material. Defaults to 'True' (optional)
    :param bool dithering: Whether material is dithered with noise. Removes banding from gradients like ones produced by lighting. Defaults to 'True' (optional)
    :param bool flatShading: Use THREE.FlatShading rather than THREE.StandardShading. (optional)
    :param bool npot: Use settings for non-power-of-two (NPOT) texture. (optional)
    :param dict offset: Texture offset to be used. Defaults to '{'x': 1, 'y': 1}' (optional)
    :param float opacity: Extent of transparency. If the transparent property is not true, then the material will remain opaque and opacity will only affect color. Defaults to '1' (optional)
    :param dict repeat: Texture repeat to be used. Defaults to '{'x': 1, 'y': 1}' (optional)
    :param str shader: Which material to use. Defaults to the standard material. Can be set to the flat material or to a registered custom shader material. Defaults to 'standard' (optional)
    :param str side: Which sides of the mesh to render. Allows [front, back, double] Defaults to 'front' (optional)
    :param str src: URI, relative or full path of an image/video file. e.g. 'store/users/wiselab/images/360falls.mp4'. (optional)
    :param bool transparent: Whether material is transparent. Transparent entities are rendered after non-transparent entities. (optional)
    :param str vertexColors: Whether to use vertex or face colors to shade the material. Allows [none, vertex, face] Defaults to 'none' (optional)
    :param bool visible: Whether material is visible. Raycasters will ignore invisible materials. Defaults to 'True' (optional)
    """
    def __init__(self, **kwargs):
        if "opacity" in kwargs:
            # kwargs["transparent"] = True # need to be transparent to be opaque
            if kwargs["opacity"] > 1.0: # keep opacity between 0.0 and 1.0
                kwargs["opacity"] = float(kwargs["opacity"]) / 100
            kwargs["opacity"] = max(0.0, kwargs["opacity"])
            kwargs["opacity"] = min(kwargs["opacity"], 1.0)

        super().__init__(**kwargs)
