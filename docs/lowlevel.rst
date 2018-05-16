.. module:: niche_vlaanderen

###################
Reference
###################

For simple calculation, the recommended way to run NICHE is through the
:ref:`niche` class, as demonstrated in the :doc:`tutorials`.

In the low level interface, it is possible to run the three classes
``Vegetation``, ``Acidity`` and ``NutrientLevel`` directly using numpy arrays.
This allows a greater flexibility and control over the details of the calculation,


.. _niche:

Niche
=====

.. autoclass:: Niche
    :members:

Niche Delta
===========

.. autoclass:: NicheDelta
    :members:

Flooding
========

.. autoclass:: Flooding
    :members:

Array based functions
=====================

At the lowest level of Niche sit a number of array-based classes which calculate the actual Niche model. These require numpy arrays as an input: all handling of gis files/... is done in the Niche class. 

NutrientLevel
-------------

.. autoclass:: NutrientLevel
    :members:

Acidity
-------

.. autoclass:: Acidity
    :members:


Vegetation
----------

.. autoclass:: Vegetation
    :members:

Example
~~~~~~~~~
The low level api can be used to calculate single values without having to
create a full grid.

 .. code-block:: pycon

     >>> import numpy as np
     >>> import niche_vlaanderen
     >>> nutrient_level = np.array([4])
     >>> acidity = np.array([3])
     >>> mlw = np.array([50])
     >>> mhw = np.array([10])
     >>> soil_codes = np.array([14])
     >>> nv = niche_vlaanderen.Vegetation()
     >>> veg_predict, veg_occurrence = nv.calculate(soil_codes,mhw,mlw,nutrient_level,acidity)
     >>> veg_occurrence
     {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0, 6: 0.0, 7: 1.0, 8: 1.0, 9: 0.0, 10: 0.0, 11: 0.0, 12: 1.0, 13: 0.0, 14: 0.0, 15: 0.0, 16: 1.0, 17: 0.0, 18: 0.0, 19: 0.0, 20: 0.0, 21: 0.0, 22: 0.0, 23: 0.0, 24: 0.0, 25: 0.0, 26: 0.0, 27: 0.0, 28: 0.0}

 De waarden die voorkomen (in 100% van het gebied, we hebben immers maar 1 pixel) zijn 7, 8, 12 en 16.

 Gebruiken we ook de waarde voor overstromingen dan wordt dit.

 .. code-block:: pycon

    >>> import numpy as np
    >>> import niche_vlaanderen
    >>> nutrient_level = np.array([4])
    >>> acidity = np.array([3])
    >>> mlw = np.array([50])
    >>> mhw = np.array([10])
    >>> soil_codes = np.array(["L1"])
    >>> nv = niche_vlaanderen.Vegetation()
    >>> veg_predict, veg_occurrence = nv.calculate(soil_codes, nutrient_level, acidity, mhw, mlw)
    >>> veg_occurrence
    {7: 1.0, 8: 1.0, 12: 1.0, 16: 1.0}

De waarden die voorkomen (in 100% van het gebied, we hebben immers maar 1 pixel) zijn 7, 8, 12 en 16.

Gebruiken we ook de waarde voor overstromingen dan wordt dit.

 .. code-block:: pycon

     >>> import numpy as np
     >>> import niche_vlaanderen
     >>> nutrient_level = np.array([4])
     >>> acidity = np.array([3])
     >>> mlw = np.array([50])
     >>> mhw = np.array([10])
     >>> soil_codes = np.array(["L1"])
     >>> nv = niche_vlaanderen.Vegetation()
     >>> inundation = np.array([1])
     >>> veg_predict, veg_occurrence = nv.calculate(soil_codes,mhw,mlw,nutrient_level,acidity,inundation=inundation)
     >>> veg_occurrence
     {7: 1.0, 12: 1.0, 16: 1.0}

 Vegetatietype 8 is nu niet meer mogelijk.

 .. code-block:: pycon

    >>> import numpy as np
    >>> import niche_vlaanderen
    >>> nutrient_level = np.array([4])
    >>> acidity = np.array([3])
    >>> mlw = np.array([50])
    >>> mhw = np.array([10])
    >>> soil_codes = np.array([14])
    >>> nv = niche_vlaanderen.Vegetation()
    >>> inundation = np.array([1])
    >>> veg_predict, veg_occurrence = nv.calculate(soil_codes,nutrient_level,acidity,mhw,mlw, inundation=inundation)
    >>> veg_occurrence
    {7: 1.0, 12: 1.0, 16: 1.0}

Vegetatietype 8 is nu niet meer mogelijk.

.. _depths.csv: https://github.com/inbo/niche_vlaanderen/blob/master/niche_vlaanderen/system_tables/floodplains/depths.csv
.. _duration.csv: https://github.com/inbo/niche_vlaanderen/blob/master/niche_vlaanderen/system_tables/floodplains/duration.csv
.. _frequency.csv: https://github.com/inbo/niche_vlaanderen/blob/master/niche_vlaanderen/system_tables/floodplains/frequency.csv

.. _`matplotlib.axes.Axes`: https://matplotlib.org/api/axes_api.html#matplotlib.axes.Axes
.. _`pandas.DataFrame`: https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.html

.. _`Using abiotic grids`: https://inbo.github.io/niche_vlaanderen/advanced_usage.html#Using-abiotic-grids
.. _`Comparing Niche Classes`: https://inbo.github.io/niche_vlaanderen/advanced_usage.rst#Comparing-Niche-classes
