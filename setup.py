import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="arena-py",
    version="0.0.1",
    author="Conix Research Center",
    author_email="info@conix.io",
    license="BSD 3-clause \"New\" or \"Revised License\"",
    description="Draw objects in the ARENA using Python!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/conix-center/ARENA-py",
    packages=setuptools.find_packages(),
    install_requires=[ "aiohttp",
                       "paho-mqtt~=1.5.0",
                       "numpy~=1.18.1",
                       "requests~=2.23.0",
                       "scipy~=1.4.1",
                       "webcolors~=1.3" ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
