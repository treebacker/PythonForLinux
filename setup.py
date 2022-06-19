import sys
import os.path
from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()


setup(
    name = "PythonForLinux",
    version = "0.0.1",
    author = 'treebacker',
    author_email = 'treebacker58@gmail.com',
    description = 'A codebase aimed to make interaction with Linux and native execution easier',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license = 'BSD',
    keywords = 'linux python',
    url = 'https://github.com/treebacker/PythonForLinux',
    packages = ['linux',
                'linux.linuxobject',
                'linux.security',
                'linux.utils'],
    classifiers = ['Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 2.7']
)