#!/usr/bin/env python
from distutils.core import setup

for cmd in ('egg_info', 'develop', 'bdist_egg'):
    import sys
    if cmd in sys.argv:
        from setuptools import setup

setup(
    name='webstruct-token',
    version='0.1',
    author='Mikhail Korobov, Terry Peng',
    author_email='kmike84@gmail.com',
    packages=['webstruct_token', 'webstruct_token.features'],
    license = 'MIT license',
)
