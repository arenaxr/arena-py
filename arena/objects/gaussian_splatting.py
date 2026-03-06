from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

@dataclass
class GaussianSplatting:
    """
    Gaussian Splat
    Load a 3D Gaussian Splat for Real-Time Radiance Field Rendering. More information: <a href='https://github.com/quadjr/aframe-gaussian-splatting'>A-Frame Gaussian Splatting</a>. See guidance to store paths under <a href='https://docs.arenaxr.org/content/interface/filestore.html'>ARENA File Store, CDN, or DropBox</a>.

    :param str object_type: 3D object type.. Must be 'gaussian_splatting'.
    :param str src: Url of the .ply or .splat file. Use File Store paths under 'store/users/username', see CDN and other storage options in the description above..
    :param str cutoutEntity: Selector to a box primitive that uses scale and position to define the bounds of splat points to render., optional. Defaults to ''
    :param float pixelRatio: Pixel ratio for rendering. Reducing the value decreases the resolution and improves performance. If a negative value is set, the device's native value will be applied., optional. Defaults to 1.0
    :param float xrPixelRatio: Same as pixelRatio. Applied to XR devices., optional. Defaults to 0.5
    """
    object_type: str
    src: str
    cutoutEntity: Optional[str] = ''
    pixelRatio: Optional[float] = 1.0
    xrPixelRatio: Optional[float] = 0.5
