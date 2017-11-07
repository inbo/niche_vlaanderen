########################
Niche Configuration file
########################

The easiest way to get started with NICHE is by using a configuration file.
For a simple NICHE model this could look like this:

 .. code-block:: yaml

     input_layers:
       mhw: data/mhw_small.asc
       mlw: data/mlw_small.asc
       soil_code: data/soil_code_small.asc

     model_options:
       simple_model: True
       deviation: False
       output_dir: _output

The file specifies the input layers, the output directory, and other model options.
In this case, as we have a simple model (:ref:`simple`), as specified in the model options.

For a full model, more input layers must be specified:

  .. csv-table:: Possible input layers for a Full Niche model
    :header-rows: 1

    key, simple model,full model, allowed values, documentation
    ``soil_code``,X, X, integer, :ref:`soil_code`
    ``mhw``,X,  X, integer, :ref:`mhw`
    ``mlw``,X, X, integer, :ref:`mlw`
    ``msw``,, X, integer, :ref:`msw`
    ``seepage``,, X, xxx, :ref:`seepage`
    ``inundation_acidity``,, X, xxx, :ref:`inundation_acidity`
    ``inundation_nutrient``,, X, xxx, :ref:`inundation_nutrient`
    ``nitrogen_atmospheric``,, X, xxx, :ref:`nitrogen_atmospheric`
    ``nitrogen_animal``,, X, xxx, :ref:`nitrogen_animal`
    ``nitrogen_fertilizer``,, X, xxx, :ref:`nitrogen_fertilizer`
    ``management``,, X, xxx, :ref:`management`
    ``conductivity``,, X, xxx, :ref:`minerality`
    ``rainwater``,, X, xxx, :ref:`rainwater`
    ``inundation_vegetation``,, \(X\) ,xxx, :ref:`inundation`
    ``management_vegetation``,,\(X\) ,xxx, :ref:`management`
    ``acidity``,,abiotic,xxx, :ref:`acidity`
    ``nutrient_level``,,abiotic ,xxx, :ref:`nutrient_level`

The values for ``inundation_vegetation`` and ``management_vegetation`` are optional.

The two abiotic values ``acidity`` and ``nutrient_level`` are normally calculated from the other input values.
You can overwrite them if you specify ``abiotic`` in the model_options.

A full example is given below:

 .. literalinclude:: ../niche_vlaanderen/system_tables/example.yaml

The option ``deviation`` creates deviation maps, which show the difference between the borders specified in the niche table and the actual values of mhw and mlw for every soil type.
