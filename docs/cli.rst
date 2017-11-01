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
In this case, as we have a :ref:`simple`, as specified in the model options.

For a full model, more input layers must be specified:

  .. csv-table:: Possible input layers for a Full Niche model
    :header-rows: 1

    key, obliged, allowed values, documentation
    ``mhw``, X, integer, :ref:`mhw`
    ``mlw``, X, integer, :ref:`mlw`
    ``msw``, X, integer, :ref:`msw`
    ``soil_code``, X, integer, :ref:`soil_code`
    ``seepage``, X, xxx, :ref:`seepage`
    ``inundation_acidity``, X, xxx, :ref:`inundation_acidity`
    ``inundation_nutrient``, X, xxx, :ref:`inundation_nutrient`
    ``nitrogen_atmospheric``, X, xxx, :ref:`nitrogen_atmospheric`
    ``nitrogen_animal``, X, xxx, :ref:`nitrogen_animal`
    ``nitrogen_fertilizer``, X, xxx, :ref:`nitrogen_fertilizer`
    ``management``, X, xxx, :ref:`management`
    ``conductivity``, X, xxx, :ref:`minerality`
    ``rainwater``, X, xxx, :ref:`rainwater`
    ``inundation_vegetation``, xxx, :ref:`inundation`
    ``management_vegetation``, xxx, :ref:`management`
    ``acidity``, xxx, :ref:`acidity`
    ``nutrient_level``, xxx, :ref:`nutrient_level`



A full example is given below:

 .. code-block:: yaml

     input_layers:
       mhw: data/mhw_small.asc
       mlw: data/mlw_small.asc
       soil_code: data/soil_code_small.asc

     model_options:
       simple_model: True
       deviation: True
       output_dir: _output

