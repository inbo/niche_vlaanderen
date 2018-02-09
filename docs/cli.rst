########################
Niche Configuration file
########################

Simple model
============

Instead of running Niche interactively, it can be used  with a configuration file.
For a simple NICHE model this could look like this:

 .. code-block:: yaml

     model_options:
       full_model: False
       deviation: False
       output_dir: _output

     input_layers:
       mhw: data/mhw_small.asc
       mlw: data/mlw_small.asc
       soil_code: data/soil_code_small.asc

The file specifies the input layers, the output directory, and other model options.
In this case, as we have a simple model (:ref:`simple`), as specified in the model options.


Full model
==========
For a full model, more input layers must be specified:

.. csv-table:: Possible input layers for a Full Niche model
    :header-rows: 1


    key, simple model,full model, documentation
    ``soil_code``,X, X,  :ref:`soil_code`
    ``mhw``,X,  X,  :ref:`mhw`
    ``mlw``,X, X,  :ref:`mlw`
    ``msw``,, X,  :ref:`msw`
    ``seepage``,, X,  :ref:`seepage`
    ``inundation_acidity``,, X,  :ref:`inundation_acidity`
    ``inundation_nutrient``,, X,  :ref:`inundation_nutrient`
    ``nitrogen_atmospheric``,, X,  :ref:`nitrogen_atmospheric`
    ``nitrogen_animal``,, X,  :ref:`nitrogen_animal`
    ``nitrogen_fertilizer``,, X,  :ref:`nitrogen_fertilizer`
    ``management``,, X,  :ref:`management`
    ``conductivity``,, X,  :ref:`minerality`
    ``rainwater``,, X,  :ref:`rainwater`
    ``inundation_vegetation``,, \(X\) , :ref:`inundation_vegetation`
    ``management_vegetation``,,\(X\) , :ref:`management`
    ``acidity``,,abiotic, :ref:`acidity`
    ``nutrient_level``,,abiotic , :ref:`nutrient_level`

The values for ``inundation_vegetation`` and ``management_vegetation`` are optional.

An example configuration file for a full model is given below.

 .. literalinclude:: full.yml


Abiotic values
==============
Using a configuration file, it is also possible to use abiotic values, like
previously demonstrated in :ref:`advanced_usage.ipynb#Using-abiotic-grids`.

To do this the values ``acidity`` and ``nutrient_level`` must be specified,
together with the ``abiotic`` model option.


Generating a config file in interactive mode
============================================

When running Niche in interactive mode, representing the model will show the
corresponding configuration file. This was demonstrated in :ref:`getting_started.ipynb#Showing-the-model-configuration`

Also when writing a grid using the write method a "log.txt" file will be written.
This file itself is also a valid configuration file for a next run.


Full example
==============

We offer a full example (included below) which contains all possible options and some documentation.
This file may be a good starting point for creating your own configuration files.

 .. literalinclude:: ../niche_vlaanderen/system_tables/example.yaml

The option ``deviation`` creates deviation maps, which show the difference between the borders specified in the niche table and the actual values of mhw and mlw for every soil type.
