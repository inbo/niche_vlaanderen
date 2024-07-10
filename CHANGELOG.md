# 2.0 (2024-07-10)

This release contains a breaking change with the 1.x version of Niche-Vlaanderen due to
the handling of the groundwater levels. Version 2.x uses groundwater levels according 
to the sign convention used in Watina, i.e. negative values for groundwater levels 
below ground. As such, previous model configurations will not work or give unexpected
results (#376).

Furthermore (no breaking change), the reference/system tables used in the package are 
linked with the official publication of the reference tables in 
[Zenodo](https://zenodo.org/doi/10.5281/zenodo.10417821). The column names of the
system tables and the translations are updated as well (#379)

A number of improvements to the code and documentation have been implemented: 
 
* Remove deprecation warnings (#372, #381) and erros (#371, #373)
* Document improvement (#374)

# 1.3 (2024-05-04)


* Fix compatibility with recent Numpy/Pandas versions, update tests to pytest (#370)
* Add support for float data type soil code rasters (#371)
* Make sure package build process correctly includes the system tables (#372)
* Provide user feedback when trying to plot a non-existing raster (#373) 
* Update and improve sphinx documentation version (#374)

# 1.2 (2023-03-09)

* Add validation module, allowing the user to compare the result of a niche model with an actual vegetation map.
* Improved speed of zonal statistics.
* Detailed plot splitting up unsuitable types to soil unsuitable/mxw unsuitable+ other conditions.
* Add support for recent Python versions (3.10 and 3.11).
* Important notice:
  * Python 2 is no longer supported. Python 3.7 is the minimum version required. >=3.9 recommended.

# 1.1 (2019-09-17)

* Work with asymmetrical cells (#204)
* Add check for new versions of niche_vlaanderen (#180)
* Fix a number of warnings for newer versions of Affine and Numpy (#207)
* New install instructions for Windows (#260)
* Important notice: 
  * This is the last version supporting Python 2. Switching to Python 3 is highly recommended.
