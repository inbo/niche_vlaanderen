############
Installation
############

Windows
=======

The recommended way of installing niche on windows uses miniconda_ for installation.
The recommended version is `64 bit with Python 3.6`__, though 32 bit and Python 2.7 should work as well.

__ https://repo.continuum.io/miniconda/Miniconda3-latest-Windows-x86_64.exe
.. _miniconda: https://conda.io/miniconda.html

The installation can proceed without administrator rights, keep the default options. After miniconda is installed,
we will proceed installing niche_vlaanderen in its own environment.

Download the file https://cdn.rawgit.com/inbo/niche_vlaanderen/master/docs/niche_env.yml to a location on
your computer.

Start the `Anaconda prompt` from the start menu

Create an environment containing niche and its dependencies. You should point to the file you just downloaded with the
correct filename (make sure you pick the correct extension).

.. code-block:: default

    (C:\Users\johan\Miniconda3) C:\Users\johan> conda env create -f c:\users\johan\Downloads\niche_env.yml

Activate the niche environment

.. code-block:: default

    (C:\Users\johan\Miniconda3) C:\Users\johan> activate niche


You can verify the installation was successful by running the cli interface

.. code-block:: default

    (C:\Users\johan\Miniconda3) C:\Users\johan> niche --help
    Usage: niche [OPTIONS] CONFIG

      Command line interface to the NICHE vegetation model

    Options:
      --example  prints an example configuration file
      --help     Show this message and exit.

Upgrading
=========

Existing installations of Niche can be updated using pip (for windows, run
from the Anaconda prompt, after downloading the environment file.
https://cdn.rawgit.com/inbo/niche_vlaanderen/master/docs/niche_env.yml

.. code-block:: default

    conda env update -f c:\users\johan\Downloads\niche_env.yml

Installing a specific version
=============================

If you want to install a specific niche version, you can install using pip:

.. code-block:: default

    pip install niche_vlaanderen==1.0b7

Alternative installation
========================
Rather than using the provided environment file, you may want to install the packages yourself,
eg if you want to work with specific versions for another package. This is currently not
the recommended installation as it requires setting an environment variable for
opening some grid files. (See :ref:`missing_gcs` for instructions).

.. code-block:: default

    conda install pandas pyyaml rasterio fiona
    pip install niche_vlaanderen==1.0b7

It is strongly recommended to install also `matplotlib` (otherwise plotting will not work):

.. code-block:: default

    conda install matplotlib

In a similar way you can add jupyter notebook (``conda install jupyter``).

Running niche
=============

Whenever you want to use niche (either from the command line or Python) you need
to start from the `Anaconda prompt` (in the start menu)
and activate the environment:

.. code-block:: default

    (C:\Users\johan\Miniconda3) C:\Users\johan> activate niche

Optionally - Jupyter Notebook
=============================

If you want to run niche_vlaanderen interactively, we recommend using a [jupyter notebook](http://jupyter.org/).
To run this, from the anaconda prompt do:

.. code-block:: default

    (C:\Users\johan\Miniconda3) C:\Users\johan> activate niche_vlaanderen
    (C:\Users\johan\Miniconda3) C:\Users\johan> jupyter notebook

This should open a webbrowser pointing towards http://localhost:8888 . If you browser does not open, try looking for the
correct URL at the anaconda prompt.

The :doc:`tutorials` will use these jupyter notebooks, and are the best place to continue from here.


