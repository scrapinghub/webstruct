#!/usr/bin/env python
from distutils.core import setup
from setuptools import find_packages

for cmd in ('egg_info', 'develop', 'bdist_egg'):
    import sys
    if cmd in sys.argv:
        from setuptools import setup

setup(
    name='webstruct',
    version='0.1',
    author='Mikhail Korobov, Terry Peng',
    author_email='kmike84@gmail.com, pengtaoo@gmail.com',
    packages=find_packages(),
    license = 'MIT license',
)
