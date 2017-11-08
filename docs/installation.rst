##################
Niche Installation
##################

Windows Installation
====================

The recommended way of installing niche on windows uses miniconda_ for installation.
The recommended version is `64 bit with Python 3.6`__, though 32 bit and Python 2.7 should work as well.

__ https://repo.continuum.io/miniconda/Miniconda3-latest-Windows-x86_64.exe
.. _miniconda: https://conda.io/miniconda.html

The installation can proceed without administrator rights, keep the default options.

Start the `Anaconda prompt` from the start menu

Install the dependant packages

.. code-block:: default

    (C:\Users\johan\Miniconda3) C:\Users\johan> conda config --add channels conda-forge
    (C:\Users\johan\Miniconda3) C:\Users\johan> conda install numpy rasterio pandas pyyaml fiona

Install niche itself (last version):

.. code-block:: default

    (C:\Users\johan\Miniconda3) C:\Users\johan> pip install git+https://github.com/INBO/niche_vlaanderen


You can verify the installation was succesful by running the cli interface

.. code-block:: default

    (C:\Users\johan\Miniconda3) C:\Users\johan> niche --help
    Usage: niche [OPTIONS] CONFIG

      Command line interface to the NICHE vegetation model

    Options:
      --example  prints an example configuration file
      --help     Show this message and exit.

