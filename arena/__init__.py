"""
arena-py

Draw objects and run programs in the ARENA using Python!
"""

__author__      = "Carnegie Mellon University"

__license__     = "BSD 3-Clause"
__maintainer__  = "WiSE Lab, Carnegie Mellon University"

try:
    from importlib import metadata
    __version__ = metadata.version("arena-py")
except Exception:
    __version__ = "unknown"

from .device import *
from .scene import *
