from .arena_object import Object


class GaussianSplatting(Object):
    """
    GaussianSplatting object class to manage its properties in the ARENA: Load a 3D Gaussian Splat for Real-Time Radiance Field Rendering. More information: <https://github.com/quadjr/aframe-gaussian-splatting> A-Frame Gaussian Splatting. See guidance to store paths under <https://docs.arenaxr.org/content/interface/filestore.html> ARENA File Store, CDN, or DropBox.

    :param str cutoutEntity: Selector to a box primitive that uses scale and position to define the bounds of splat points to render. (optional)
    :param float pixelRatio: Pixel ratio for rendering. Reducing the value decreases the resolution and improves performance. If a negative value is set, the device's native value will be applied. Defaults to '1.0' (optional)
    :param str src: Use File Store paths under 'store/users/username', see CDN and other storage options in the description above. (optional)
    :param float xrPixelRatio: Same as pixelRatio. Applied to XR devices. Defaults to '0.5' (optional)
    """
    object_type = "gaussian_splatting"

    def __init__(self, **kwargs):
        super().__init__(object_type=GaussianSplatting.object_type, **kwargs)
