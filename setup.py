#!/usr/bin/env python
from setuptools import setup, find_packages

version = '0.5'

setup(
    name='webstruct',
    version=version,
    description="A library for creating statistical NER systems that work on HTML data",
    long_description=open('README.rst').read(),
    author='Mikhail Korobov, Terry Peng',
    author_email='kmike84@gmail.com, pengtaoo@gmail.com',
    url='https://github.com/scrapinghub/webstruct',
    packages=find_packages(),
    license='MIT',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Text Processing :: Linguistic",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
    install_requires=['six', 'lxml', 'scikit-learn', 'tldextract', 'requests'],
)
