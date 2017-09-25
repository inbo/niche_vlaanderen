#################
Code Tables
#################

.. _soil_codes:

soil_codes
==========

The table `soil_codes.csv <https://github.com/INBO/niche_vlaanderen/blob/master/SystemTables/soil_codes.csv>`_ contains the supported soil_codes in NICHE and their corresponding `soil_group` (used in determining the soil_glg_class, :ref:`soil_glg_class`).

.. _management_codes:

management_codes
================

The table `management_codes.csv  <https://github.com/INBO/niche_vlaanderen/blob/master/SystemTables/management_codes.csv>`_ contains the supported management_codes in NICHE.
It also contains a column `influence` which is used in the calculation of nutrient level.

niche_vlaanderen
================

The table `niche_vlaanderen.csv <https://github.com/INBO/niche_vlaanderen/blob/master/SystemTable/niche_vlaandersn.csv>`_ contains the link between the vegetation types that can be predicted by niche and the location factors that govern them.

Required columns are:
 * veg_code: vegetation code
 * soil_code: soil code, must correspond to the :ref:`soil_codes`:.
 * nutrient_level
 * acidity
 * mhw_min, mhw_max:
 * mlw_min, mlw_max:
 * managament
 * inundation

Other columns can exist but are ignored.
