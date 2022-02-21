import os

from setuptools import setup

with open("../README.md", "r") as fh:
    long_description = fh.read()

setupDirectory = os.path.dirname(os.path.realpath(__file__))

setup(
    name="hypergol",
    version=open('../version', 'rt').read().strip(),
    author="Laszlo Sragner",
    author_email="hypergol.developer@gmail.com",
    description="An opinionated multithreaded Data Science framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hypergol/hypergol",
    packages=['hypergol', 'hypergol.cli'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    install_requires=['fire', 'Jinja2', 'GitPython', 'numpy==1.19.2', 'tensorflow==2.5.0', 'torch==1.10.2', 'tqdm', 'pydantic', 'fastapi', 'uvicorn'],
    include_package_data=True
)
