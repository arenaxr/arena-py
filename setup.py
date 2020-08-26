import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ARENA-py",
    version="0.0.1",
    author="Conix Research Center",
    author_email="info@conix.io",
    description="Draw objects in the ARENA using python.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/conix-center/ARENA-py",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD 3-Clause \"New\" or \"Revised\" License (BSD-3-Clause)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
