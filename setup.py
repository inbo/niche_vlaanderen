#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from setuptools import setup
from pathlib import Path


version = {}

long_description = (Path(__file__).parent / "README.rst").read_text()
with open("niche_vlaanderen/version.py") as fp:
    exec(fp.read(), version)

with open('README.rst') as readme_file:
    readme = readme_file.read()

requirements = [
        'pandas',
        'numpy',
        'matplotlib',
        'rasterio',
        'pyyaml',
        'rasterstats>=0.17',
        'tqdm',
        'pygeos',
        'geopandas'
        ]

setup(name='niche_vlaanderen',
    version=version['__version__'],
    description='NICHE Vlaanderen: hydro-ecological model for valley-ecosystems in Flanders',
    url='https://github.com/inbo/niche_vlaanderen',
    author='Johan Van de Wauw',
    author_email='johan.vandewauw@inbo.be',
    license='MIT',
    install_requires=requirements,
    packages=["niche_vlaanderen", "niche_vlaanderen.system_tables",
              "niche_vlaanderen.system_tables.flooding"],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
    ],
    include_package_data=True,
    long_description=long_description,
    long_description_content_type="text/x-rst",
    tests_require=['pytest'],
    entry_points='''
        [console_scripts]
        niche=niche_vlaanderen.cli:cli
    '''
)
