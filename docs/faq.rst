##########################
Frequently Asked Questions
##########################

This page lists a few known problems that may occur during the installation
or usage of niche_vlaanderen, and workarounds for them.

If your issue is not mentioned in this list, please search for the issues on
our issuetracker_, and file a new issue if it is needed.

.. _missing_gcs:

Missing gcs.csv file
====================

If you see the following issue:

.. code-block:: default

   ERROR:rasterio._gdal:CPLE_OpenFailed in b'Unable to open EPSG support file gcs.csv.
   Try setting the GDAL_DATA environment variable to point to the
   directory containing EPSG csv files.'

This is a known issue of rasterio in conda. As a workaround, from the anaconda
prompt, try setting the GDAL_DATA environment to a path which contains a
``gcs.csv`` file (use search to find a path).

.. code-block:: default

   set GDAL_DATA=C:\Users\johan\Miniconda3\pkgs\gdal-2.1.3-py36_vc14_7\Library\share\gdal\gcs.csv

And then start python, niche (command line) or jupyter notebook.

.. code-block:: default

   set GDAL_DATA=C:\Users\johan\Miniconda3\pkgs\gdal-2.1.3-py36_vc14_7\Library\share\gdal\gcs.csv
   jupyter notebook

You can also set the environment variable in windows itself. In that case, it is no longer needed to run the
`set GDAL_DATA= ...`command.
To do this, follow these steps:

 1) right click the `my computer` icon in windows. And choose the last option "properties".

  .. image:: _static/png/system_properties.png
     :scale: 50%

 2) On the left, choose the lower option ("advanced properties")

  .. image:: _static/png/advanced_properties.png
     :scale: 50%

 3) In the next dialog, make sure you select the "advanced" tab. On the button right
    there should be a button with "Environment Variables" ("Omgevingsvariabelen").

  .. image:: _static/png/advanced_properties2.png
     :scale: 50%

 4) In the next dialog, Add a new user variable (if you are admin, you can add a system variable,
    that way the configuration will apply to all users of the computer).

  .. image:: _static/png/environment_variables.png
     :scale: 50%

  5) Add the name "GDAL_DATA" and the path to a place where the gcs.csv file can be found
     (Use search to find it). Don't include the filename.

  .. image:: _static/png/new_environment_variable.png
     :scale: 50%

  6) Anaconda prompt must be restarted to find the variable.

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
a geotiff from arcgis. This format is best supported by the library we use
for raster analysis.

.. _issuetracker: https://github.com/inbo/niche_vlaanderen/issues
