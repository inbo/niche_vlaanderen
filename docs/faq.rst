##########################
Frequently Asked Questions
##########################

This page lists a few known problems that may occur during the installation
or usage of niche_vlaanderen, and workarounds for them.

If your issue is not mentioned in this list, please search for the issues on
our issuetracker_, and file a new issue if it is needed.

Missing gcs.csv file
====================

.. code-block:: default

   ERROR:rasterio._gdal:CPLE_OpenFailed in b'Unable to open EPSG support file gcs.csv.
   Try setting the GDAL_DATA environment variable to point to the
   directory containing EPSG csv files.'

This is a known issue of rasterio in conda. As a workaround, from the anaconda
prompt, try setting the GDAL_DATA environment to a path which contains a
``gcs.csv`` file (use search to find a path).

.. code-block:: default

   set GDAL_DATA=%APPDATA%xxx

And then start python, niche (command line) or jupyter notebook.

.. code-block:: default

   set GDAL_DATA=%APPDATA%xxx
   jupyter notebook

Using ESRI grids without sta.adf
================================

.. code-block:: default

  Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/home/johan/_proj/niche/niche_vlaanderen/niche_vlaanderen/niche.py", line 192, in set_input
    with rasterio.open(value) as dst:
  File "/home/johan/.local/lib/python3.5/site-packages/rasterio/__init__.py", line 193, in open
    s.start()
  File "rasterio/_base.pyx", line 76, in rasterio._base.DatasetReader.start (rasterio/_base.c:2969)
  rasterio.errors.RasterioIOError: 'bodemveen' not recognized as a supported file format.


In general ESRI grids can be opened by specifying the directory of the files
or by choosing one of the *.ADF files in the directory. However if the 'sta.adf'
file is missing, the file can not be opened in niche (it will also fail in QGis
or other gdal-based applications). In that case, try exporting the grid to
a geotiff from arcgis.

.. _issuetracker: https://github.com/inbo/niche_vlaanderen/issues