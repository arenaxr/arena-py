import setuptools

with open("README.md", "r") as readme:
    long_description = readme.read()

setuptools.setup(
    name="arena-py",
    version="0.1.24",
    author="Conix Research Center",
    author_email="info@conix.io",
    license="BSD 3-clause \"New\" or \"Revised License\"",
    description="Draw objects and run programs in the ARENA using Python!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/conix-center/ARENA-py",
    packages=setuptools.find_packages(),
    install_requires=[
        "aiohttp>=3.7.4",
        "paho-mqtt~=1.5.0",
        "numpy~=1.20.1",
        "requests~=2.23.0",
        "scipy~=1.6.1",
        "webcolors~=1.3",
        "google_auth_oauthlib~=0.4.2",
        "PyJWT~=2.0.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
