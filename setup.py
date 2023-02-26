from setuptools import setup, find_packages

setup(
<<<<<<< HEAD
    name="BT-diagrams",
    version="0.0.11",
=======
    name="MT-diagrams",
    version="0.0.1",
>>>>>>> master
    description="Thesis project",
    author="Nikolai Perlt",
    author_email="npe@itu.dk",
    url="https://github.com/Perlten/MT-diagrams",
    packages=find_packages(),
    long_description="This is the long description",
    install_requires=["plantuml", "typer", "astroid", "six", "requests", "jsonschema"],
    classifiers=[
        "Programming Language :: Python :: 3.10",
    ],
    entry_points={
        "console_scripts": [
            "mt-diagrams=src.cli_interface:main",
        ],
    },
)
