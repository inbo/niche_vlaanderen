############
Installation
############

Windows
=======

The recommended way of installing niche_vlaanderen on windows uses miniconda_ for installation.
The recommended version is `64 bit with Python 3.9`__.

__ https://repo.anaconda.com/miniconda/Miniconda3-py39_4.12.0-Windows-x86_64.exe
.. _Miniconda: https://conda.io/miniconda.html

The installation can proceed without administrator rights, keep the default options. After miniconda is installed,
we will proceed installing niche_vlaanderen in its own environment.

Start the `Anaconda prompt` from the start menu

You will probably see something as:

.. code-block:: shell

    (C:\Users\myusername\Miniconda3) C:\Users\myusername> 
  OR
    (base) C:\Users\myusername> 

Create an environment (called niche in this example) that will contain niche_vlaanderen and its dependencies:

.. code-block:: shell

    (C:\Users\myusername\Miniconda3) C:\Users\myusername> conda create --name niche

Activate the niche environment:

.. code-block:: shell

    (C:\Users\myusername\Miniconda3) C:\Users\myusername> conda activate niche

You will see that `(C:\\Users\\myusername\\Miniconda3)`/`(base)` will change into `(niche)`.

Now install the niche_vlaanderen package and its dependencies within the niche environment:

.. code-block:: shell

    (niche) C:\Users\myusername> conda install pandas pyyaml rasterio fiona
    (niche) C:\Users\myusername> pip install niche_vlaanderen

It is strongly recommended to install also `matplotlib` (otherwise plotting
will not work) and `jupyter` notebook, which allows interactive usage from a web browser.

.. code-block:: shell

    (niche) C:\Users\myusername> conda install matplotlib jupyter

You can verify the installation was successful by running the command line interface.
Note you must activate niche once more, because some changes were made during
installation.

.. code-block:: shell

    (C:\Users\myusername\Miniconda3) C:\Users\myusername> conda activate niche
    (niche) C:\Users\myusername> niche --help
    Usage: niche [OPTIONS] CONFIG

      Command line interface to the NICHE vegetation model

    Options:
      --example  prints an example configuration file
      --version  prints the version number
      --help     Show this message and exit.

Upgrading
=========

Existing installations of niche_vlaanderen can be updated using pip (run
from the Anaconda prompt).

.. code-block:: shell

    (C:\Users\myusername\Miniconda3) C:\Users\myusername> conda activate niche
    (niche) C:\Users\myusername> pip install niche_vlaanderen --upgrade
    
Note you might need to update other packages.

Installing a specific version
=============================

If you want to install a specific niche_vlaanderen version, you can install using pip:

.. code-block:: shell

    (C:\Users\myusername\Miniconda3) C:\Users\myusername> conda activate niche
    (niche) C:\Users\myusername> pip install niche_vlaanderen==1.0

Alternative installation
========================
It is possible to install niche_vlaanderen without using an environment. This is currently not
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

Whenever you want to use niche_vlaanderen (either from the command line or Python) you need
to start from the `Anaconda prompt` (in the start menu)
and activate the environment:

.. code-block:: shell

    (C:\Users\myusername\Miniconda3) C:\Users\myusername> conda activate niche

Optionally - Jupyter Notebook
=============================

If you want to run niche_vlaanderen interactively, we recommend using a [jupyter notebook](http://jupyter.org/).
To run this, from the `Anaconda prompt` do:

.. code-block:: default

    (C:\Users\myusername\Miniconda3) C:\Users\myusername> conda activate niche
    (niche) C:\Users\myusername> jupyter notebook

This should open a webbrowser pointing towards http://localhost:8888 . If your browser does not open, try looking for the correct URL at the `Anaconda prompt`.

The :doc:`tutorials` will use these jupyter notebooks, and are the best place to continue from here.


