import os

import setuptools

with open("README.md", "r") as readme:
    long_description = readme.read()

# package_root = os.path.abspath(os.path.dirname(__file__))

# version = {}
# with open(os.path.join(package_root, "arena/version.py")) as fp:
#     exec(fp.read(), version)
# version = version["__version__"]

setuptools.setup(
    name="arena-py",
    version="1.4.0",
    author="Carnegie Mellon University",
    author_email="arenaxr@andrew.cmu.edu",
    license="BSD 3-clause \"New\" or \"Revised License\"",
    description="Draw objects and run programs in the ARENA using Python!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/arenaxr/arena-py",
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            'arena=arena.__main__:cli',
            'arena-py-permissions=arena.scripts.arena_py_permissions:main',
            'arena-py-pub=arena.scripts.arena_py_pub:main',
            'arena-py-signout=arena.scripts.arena_py_signout:main',
            'arena-py-sub=arena.scripts.arena_py_sub:main',
            'arena-py-token=arena.scripts.arena_py_token:main'
        ],
    },
    # Goal: keep dependencies minimal to increase portability to platforms like RustPython
    install_requires=[
        "paho-mqtt~=2.1.0",
        "opentelemetry-exporter-otlp-proto-grpc==1.21.*",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
)
