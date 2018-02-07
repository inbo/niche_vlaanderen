##################
Niche Installation
##################

Windows Installation
====================

The recommended way of installing niche on windows uses miniconda_ for installation.
The recommended version is `64 bit with Python 3.6`__, though 32 bit and Python 2.7 should work as well.

__ https://repo.continuum.io/miniconda/Miniconda3-latest-Windows-x86_64.exe
.. _miniconda: https://conda.io/miniconda.html

The installation can proceed without administrator rights, keep the default options. After miniconda is installed,
we will proceed installing niche_vlaanderen in its own environment.

Download the file https://raw.githubusercontent.com/inbo/niche_vlaanderen/master/docs/niche_env.yml to a location on
your computer.

Start the `Anaconda prompt` from the start menu

Create an environment containing niche and its dependencies. You should point to the file you just downloaded with the
correct filename (make sure you pick the correct extension).

.. code-block:: default

    (C:\Users\johan\Miniconda3) C:\Users\johan> conda env create -f c:\users\johan\Downloads\niche_env.yml.txt

Activate the niche environment

.. code-block:: default

    (C:\Users\johan\Miniconda3) C:\Users\johan> activate niche_vlaanderen


You can verify the installation was successful by running the cli interface

.. code-block:: default

    (C:\Users\johan\Miniconda3) C:\Users\johan> niche --help
    Usage: niche [OPTIONS] CONFIG

      Command line interface to the NICHE vegetation model

    Options:
      --example  prints an example configuration file
      --help     Show this message and exit.

Upgrading the Installation
==========================

Existing installations of Niche can be updated using pip (for windows, run
from the Anaconda prompt

.. code-block:: default

    conda env update -f c:\users\johan\Downloads\niche_env.yml.txt

Installing a specific niche version
===================================

If you want to install a specific niche version, you can install using pip:

.. code-block:: default

    pip install niche_vlaanderen==1.0a9


Running niche
=============

Whenever you want to use niche (either from the command line or Python) you need to start from the `Anaconda prompt`
and activate the environment:

.. code-block:: default

    (C:\Users\johan\Miniconda3) C:\Users\johan> activate niche_vlaanderen
