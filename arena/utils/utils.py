# simple general purpose functions
import functools
import os
import sys
import sysconfig
import warnings

from . import not_numpy as np

_YELLOW = "\033[93m"
_RESET = "\033[0m"

# Install a custom showwarning that colours DeprecationWarning in yellow.
_orig_showwarning = warnings.showwarning


def _showwarning_yellow(message, category, filename, lineno, file=None, line=None):
    if issubclass(category, DeprecationWarning):
        out = file if file is not None else sys.stderr
        out.write(f"{_YELLOW}{warnings.formatwarning(message, category, filename, lineno, line)}{_RESET}")
    else:
        _orig_showwarning(message, category, filename, lineno, file, line)


warnings.showwarning = _showwarning_yellow


# Trailing separator, so that a sibling directory sharing the prefix (arena_robot,
# arena_helpers, ...) is not mistaken for part of arena-py.
_PACKAGE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + os.sep


def _external_code_dirs():
    """Directory prefixes of code that is neither arena-py nor the calling program:
    the standard library and installed packages."""
    dirs = set()
    try:
        paths = sysconfig.get_paths()
    except Exception:  # pragma: no cover - interpreter without full sysconfig
        paths = {}
    for key in ("stdlib", "platstdlib", "purelib", "platlib"):
        path = paths.get(key)
        if path:
            dirs.add(os.path.abspath(path) + os.sep)
    return tuple(sorted(dirs))


_EXTERNAL_CODE_DIRS = _external_code_dirs()


def warn_deprecated(msg):
    """Emit a DeprecationWarning for a deprecated key, keyword argument or member.

    The warning is attributed to the first frame belonging to the calling program.
    arena-py's own frames are skipped, so the warning points at the code that has to
    change, and standard-library and installed-package frames are skipped too, so a
    deprecated name reached through a stdlib callback (an asyncio callback, a thread
    bootstrap) is not blamed on the standard library. Attribution matters twice
    over: Python's default filters only show a DeprecationWarning raised from the
    running program, and warnings records its already-warned registry in the globals
    of whichever module it attributes to. When the stack holds no frame of the
    calling program, the warning is attributed to arena-py itself.

    Use this where the deprecated name is handled several calls deep; where the
    caller reaches the deprecated name directly, use the @deprecated decorator,
    which routes through here.
    """
    getframe = getattr(sys, "_getframe", None)
    if getframe is None:
        # Interpreters without frame introspection (arena-py also targets
        # RustPython/wasm): warn from our immediate caller without walking.
        warnings.warn(msg, DeprecationWarning, stacklevel=3)
        return
    frame = getframe(1)
    stacklevel = 2  # the stacklevel that names `frame`
    while frame is not None:
        filename = frame.f_code.co_filename
        if not filename.startswith("<frozen "):
            filename = os.path.abspath(filename)
            if not filename.startswith(_PACKAGE_DIR) and not filename.startswith(_EXTERNAL_CODE_DIRS):
                warnings.warn(msg, DeprecationWarning, stacklevel=stacklevel)
                return
        frame = frame.f_back
        stacklevel += 1
    warnings.warn(msg, DeprecationWarning, stacklevel=2)


def _announced_by_derived_class(cls, declaring_cls, msg):
    """True when a class derived from declaring_cls already announced msg for the
    construction in progress. The __init__ wrappers run from the most derived class
    downwards, so a message declared further down the MRO has already been emitted."""
    for ancestor in cls.__mro__:
        if ancestor is declaring_cls:
            return False
        if msg in ancestor.__dict__.get("__arena_deprecated_msgs__", ()):
            return True
    return False


def deprecated(msg):
    """Decorator to mark a function, property accessor, or class as deprecated.

    A decorated function or property accessor emits a DeprecationWarning with the
    given message each time it is called, and carries the message as
    ``__arena_deprecated__`` so that a deprecated member can be told apart from any
    other one; ``BaseObject.__getitem__`` uses that marker to decide which
    properties dict-style access reaches.

    A decorated class emits its message when an instance is constructed. Each
    distinct message is emitted once per construction, so a deprecated subclass of a
    deprecated class reports both the class change and the attribute change without
    repeating either, and applying this decorator twice to one class with the same
    message is a no-op the second time. A class records its own messages in
    ``__arena_deprecated_msgs__``.

    Warnings go through warn_deprecated, which attributes them to the caller.
    """
    def decorator(func_or_class):
        if isinstance(func_or_class, type):
            if msg in func_or_class.__dict__.get("__arena_deprecated_msgs__", ()):
                # This class already announces this exact message: a second wrapper
                # would emit it twice per construction, and each distinct message is
                # reported once. Applying the decorator again is a no-op per message.
                return func_or_class
            # Class decorator: wrap __init__
            orig_init = func_or_class.__init__
            @functools.wraps(orig_init)
            def new_init(self, *args, **kwargs):
                # One warning per distinct message per construction: a more derived
                # deprecated class announcing this same message has already warned.
                if not _announced_by_derived_class(type(self), func_or_class, msg):
                    warn_deprecated(msg)
                orig_init(self, *args, **kwargs)
            func_or_class.__init__ = new_init
            # The class's own messages, so a base class can tell whether a class
            # derived from it has already announced the same message.
            func_or_class.__arena_deprecated_msgs__ = (
                *func_or_class.__dict__.get("__arena_deprecated_msgs__", ()),
                msg,
            )
            return func_or_class
        else:
            # Function / property accessor decorator
            @functools.wraps(func_or_class)
            def wrapper(*args, **kwargs):
                warn_deprecated(msg)
                return func_or_class(*args, **kwargs)
            # Marker for dict-style access, see BaseObject.__getitem__.
            wrapper.__arena_deprecated__ = msg
            return wrapper
    return decorator


class Utils(object):
    @classmethod
    def tuple_to_string(cls, tup, sep=" "):
        """Turns a tuple into a string."""
        s = ""
        for val in tup:
            s += str(val) + sep
        return s.strip()

    @classmethod
    def agran(cls, float_num):
        """Reduces floating point numbers to ARENA granularity."""
        if isinstance(float_num, str):
            try:
                float_num = float(float_num)
            except:
                pass
        return round(float_num, 3)

    @classmethod
    def dict_key_replace(cls, d, key, new_key):
        """Replaces a key,val with a new key,val."""
        if key in d:
            ref = d[key]
            del d[key]
            d[new_key] = ref
        return d

    @classmethod
    def quat_to_matrix3(cls, rotq):
        x, y, z, w = rotq

        # Compute matrix elements
        xx, xy, xz = x * x, x * y, x * z
        yy, yz, zz = y * y, y * z, z * z
        wx, wy, wz = w * x, w * y, w * z

        # Rotation matrix
        rot_matrix = np.array(
            [
                [1 - 2 * (yy + zz), 2 * (xy - wz), 2 * (xz + wy)],
                [2 * (xy + wz), 1 - 2 * (xx + zz), 2 * (yz - wx)],
                [2 * (xz - wy), 2 * (yz + wx), 1 - 2 * (xx + yy)],
            ]
        )

        return rot_matrix

    @classmethod
    def matrix3_to_quat(cls, rotm):
        m00, m01, m02 = rotm[0, 0], rotm[0, 1], rotm[0, 2]
        m10, m11, m12 = rotm[1, 0], rotm[1, 1], rotm[1, 2]
        m20, m21, m22 = rotm[2, 0], rotm[2, 1], rotm[2, 2]

        # Compute quaternion components
        w = np.sqrt(max(0, 1 + m00 + m11 + m22)) / 2
        x = np.sqrt(max(0, 1 + m00 - m11 - m22)) / 2
        y = np.sqrt(max(0, 1 - m00 + m11 - m22)) / 2
        z = np.sqrt(max(0, 1 - m00 - m11 + m22)) / 2

        x = np.copysign(x, m21 - m12)
        y = np.copysign(y, m02 - m20)
        z = np.copysign(z, m10 - m01)

        return np.array([x, y, z, w])

    @classmethod
    def pose_to_matrix4(cls, pos, rotq, scale=(1, 1, 1)):  # Def arg not mutated
        mat = np.identity(4)
        mat[0:3, 0:3] = cls.quat_to_matrix3([rotq.x, rotq.y, rotq.z, rotq.w])
        mat[0:3, 3] = [pos.x, pos.y, pos.z]
        if scale != (1, 1, 1):
            scale_mat = np.identity(4)
            scale_mat[0:3, 0:3] = np.diag(scale)
            mat = mat @ scale_mat
        return mat

    @classmethod
    def matrix4_to_pose(cls, mat):
        pos = mat[0:3, 3]
        rotq = cls.matrix3_to_quat(mat[0:3, 0:3])
        scale = np.sqrt(np.sum(mat[0:3, 0:3] ** 2, axis=0))
        return pos, rotq, scale

    @classmethod
    def get_world_pose(cls, obj, scene):
        current_obj = obj
        matrices = []
        while "parent" in current_obj.data:
            current_matrix = cls.pose_to_matrix4(
                current_obj.data.position,
                current_obj.data.rotation.quaternion,
                current_obj.data.scale.array,
            )
            matrices = [current_matrix] + matrices  # prepend
            current_obj = scene.all_objects[current_obj.data.parent]
        final_matrix = np.identity(4)
        for matrix in matrices:
            final_matrix = final_matrix @ matrix
        return cls.matrix4_to_pose(final_matrix)
