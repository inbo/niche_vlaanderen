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
