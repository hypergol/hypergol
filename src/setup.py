import os
from pip._internal.network.session import PipSession
from pip._internal.req import parse_requirements
from setuptools import find_packages
from setuptools import setup


with open("../README.md", "r") as fh:
    long_description = fh.read()

setupDirectory = os.path.dirname(os.path.realpath(__file__))

setup(
    name="hypergol",
    version="0.0.1",
    author="Example Author",
    author_email="author@example.com",
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requres=['fire', 'jinja2']
)
