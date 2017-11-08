.. module:: niche_vlaanderen

#######################
Running Niche in Python
#######################

To run the niche module in Python, one has to take the following steps:

 * Initialize the model (create a ``Niche`` object)
 * Add the different input grids (or constant values) to the model (``set_input`` method)
 * Run the model (``run`` method)
 * Save the results (``write`` method).

These steps are mirrored in the design of the ``Niche`` class which is given below.

Optionally the user can also create difference maps showing how much MHW/MLW has
to change to allow a certain vegetation type. This is done using the ``deviation`` parameter of the ``run`` method.

.. autoclass:: Niche
    :members:

Example
=======

 .. code-block:: pycon

      >>> import niche_vlaanderen
      >>>
      >>> myniche = niche_vlaanderen.Niche()
      >>> myniche.set_input("msw","Input/GXG/gvg_0_cm.asc")
      >>> myniche.set_input("mlw","Input/GXG/glg_0_cm.asc")
      >>> myniche.set_input("mhw", "Input/GXG/ghg_0_cm.asc")
      >>> myniche.set_input("seepage", "Input/GXG/kwel_mm_dag.asc")
      >>>
      >>> myniche.set_input("management", "Input/Beheer/beheer_int")
      >>> myniche.set_input("soil_code", "Input/Bodem/bodemv")
      >>>
      >>> myniche.set_input("nitrogen_atmospheric", "Input/Atmosf_depositie/depositie_def")
      >>> myniche.set_input("nitrogen_animal", "Input/Bemesting/bemest_dier")
      >>> myniche.set_input("nitrogen_fertilizer", "Input/Bemesting/bemest_kunst")
      >>>
      >>> myniche.set_input("inundation_vegetation", "Input/Overstromingen/overstr_veg")
      >>> myniche.set_input("inundation_acidity", "Input/Overstromingen/ovrstr_t10_50")
      >>> myniche.set_input("inundation_nutrient", "Input/Overstromingen/ovrstr_t10_50")
      >>>
      >>> myniche.set_input("conductivity", "Input/Mineraalrijkdom/minrijkdom_")
      >>>
      >>> myniche.set_input("rainwater", "Input/nullgrid.asc")
      >>>
      >>> myniche.run()
         occurrence
      2      0.62%
      3      5.72%
      4      0.43%
      5      2.12%
      6      0.05%
      7      7.13%
      8     18.47%
      9      0.86%
      12     1.13%
      15     0.14%
      16     0.22%
      17     0.34%
      18    16.18%
      19     0.03%
      20     5.20%
      21    10.47%
      28     0.04%
      >>> myniche.write("output") # schrijft de nicheresultaten weg in een map "output"


