#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from setuptools import setup, find_packages

version = {}
with open("niche_vlaanderen/version.py") as fp:
    exec(fp.read(), version)

with open('README.rst') as readme_file:
    readme = readme_file.read()

requirements = [
        'pandas',
        'numpy',
        'rasterio',
        'pyyaml',
        'rasterstats'
        ]

setup(name='niche_vlaanderen',
    version=version['__version__'],
    description='NICHE Vlaanderen: hydro-ecological model for valley-ecosystems in Flanders',
    url='https://github.com/INBO/niche_vlaanderen',
    author='Johan Van de Wauw',
    author_email='johan.vandewauw@inbo.be',
    license='MIT',
    install_requires=requirements,
    packages=['niche_vlaanderen'],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
    "Programming Language :: Python :: 2",
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    ],
    include_package_data=True,
    tests_require=['pytest'],
    entry_points='''
        [console_scripts]
        niche=niche_vlaanderen.cli:cli
    '''
)
