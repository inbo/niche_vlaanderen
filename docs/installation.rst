############
Installation
############

Windows
=======

The recommended way of installing niche_vlaanderen on windows uses miniconda_ for installation.
The currently recommended version is `64 bit with Python 3.11`__.

__ https://repo.anaconda.com/miniconda/Miniconda3-py311_24.7.1-0-Windows-x86_64.exe
.. _Miniconda: https://docs.anaconda.com/miniconda/

The installation can proceed without administrator rights, keep the default options. After miniconda is installed,
we will proceed installing niche_vlaanderen in its own environment.

Start the `Anaconda prompt` from the start menu

You will probably see something as:

.. code-block:: shell

    (C:\Users\myusername\Miniconda3) C:\Users\myusername> 
  OR
    (base) C:\Users\myusername> 

For the remainder, we use ``(<CONDA-ENV-NAME>) C:\>`` to indicate the prompt.

.. Note::
   If you do not use the installation of Miniconda with the default Python version of 3.11
   (the python version in your ``base`` environment is not Python 3.11), you can still
   create an environment with Python 3.11 by running the following command::

       conda create -n py311 python=3.11

   By running the commands below, you will still install niche_vlaanderen in an environment
   `niche` with Python 3.11.

Create an environment (called ``niche``) that will contain niche_vlaanderen and its dependencies:

.. code-block:: shell

    (base) C:\> conda env create -f environment.yml

Activate the niche environment:

.. code-block:: shell

    (base) C:\> conda activate niche

You will see that `(C:\\Users\\myusername\\Miniconda3)`/`(base)` will change into `(niche)`.

Now install the niche_vlaanderen package within the niche environment (with the option ``--no-deps``
to avoid installing dependencies that are already in the environment):

.. code-block:: shell

    (niche) C:\> pip install niche-vlaanderen --no-deps

You can verify the installation was successful by running the command line interface.
Note you must activate niche once more, because some changes were made during
installation.

.. code-block:: shell

    (base) C:\> conda activate niche
    (niche) C:\> niche --help
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

    (base) C:\> conda activate niche
    (niche) C:\> pip install niche_vlaanderen --upgrade  --no-deps
    
Note you might need to update other packages.

Installing a specific version
=============================

If you want to install a specific niche_vlaanderen version, you can install using pip:

.. code-block:: shell

    (base) C:\> conda activate niche
    (niche) C:\> pip install niche_vlaanderen==1.0

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

