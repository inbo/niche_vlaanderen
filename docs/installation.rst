############
Installation
############

Windows
=======

The recommended way of installing niche on windows uses miniconda_ for installation.
The recommended version is `64 bit with Python 3.7`__.

__ https://repo.continuum.io/miniconda/Miniconda3-4.7.10-Windows-x86_64.exe
.. _Miniconda: https://conda.io/miniconda.html

The installation can proceed without administrator rights, keep the default options. After miniconda is installed,
we will proceed installing niche_vlaanderen in its own environment.

Start the `Anaconda prompt` from the start menu

Create an environment that will contain niche and its dependencies.

.. code-block:: shell

    (C:\Users\johan\Miniconda3) C:\Users\johan> conda create --name niche

Activate the niche environment

.. code-block:: shell

    (C:\Users\johan\Miniconda3) C:\Users\johan> activate niche

And install niche and it's dependencies

.. code-block:: shell

    conda install pandas pyyaml rasterio fiona
    pip install niche_vlaanderen

It is strongly recommended to install also `matplotlib` (otherwise plotting
will not work) and `jupyter` notebook, which allows interactive usage from a web browser.

.. code-block:: shell

    conda install matplotlib jupyter

You can verify the installation was successful by running the cli interface.
Note you must activate niche once more, because some changes were made during
installation.

.. code-block:: shell

    (C:\Users\johan\Miniconda3) C:\Users\johan> activate niche
    (niche) C:\Users\johan> niche --help
    Usage: niche [OPTIONS] CONFIG

      Command line interface to the NICHE vegetation model

    Options:
      --example  prints an example configuration file
      --version  prints the version number
      --help     Show this message and exit.

Upgrading
=========

Existing installations of Niche can be updated using pip (for windows, run
from the Anaconda prompt, after downloading the environment file.
https://cdn.rawgit.com/inbo/niche_vlaanderen/master/docs/niche_env.yml

.. code-block:: shell

    pip install niche_vlaanderen --upgrade

Installing a specific version
=============================

If you want to install a specific niche version, you can install using pip:

.. code-block:: shell

    (C:\Users\johan\Miniconda3) C:\Users\johan> activate niche
    (niche) C:\Users\johan> pip install niche_vlaanderen==1.0

Alternative installation
========================
It is possible to install niche without using an environment. This is currently not
the recommended installation as it requires setting an environment variable for
opening some grid files. (See :ref:`missing_gcs` for instructions).

.. code-block:: shell

    conda install pandas pyyaml rasterio fiona
    pip install niche_vlaanderen

Like for the normal installation, it is strongly recommended to install also `matplotlib` (otherwise plotting
will not work) and `jupyter` notebook, which allows interactive usage from a web browser.

.. code-block:: shell

    conda install matplotlib jupyter

Running niche
=============

Whenever you want to use niche (either from the command line or Python) you need
to start from the `Anaconda prompt` (in the start menu)
and activate the environment:

.. code-block:: shell

    (C:\Users\johan\Miniconda3) C:\Users\johan> activate niche

Optionally - Jupyter Notebook
=============================

If you want to run niche_vlaanderen interactively, we recommend using a [jupyter notebook](http://jupyter.org/).
To run this, from the anaconda prompt do:

.. code-block:: default

    (C:\Users\johan\Miniconda3) C:\Users\johan> activate niche
    (niche) C:\Users\johan> jupyter notebook

This should open a webbrowser pointing towards http://localhost:8888 . If you browser does not open, try looking for the
correct URL at the anaconda prompt.

The :doc:`tutorials` will use these jupyter notebooks, and are the best place to continue from here.


