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

