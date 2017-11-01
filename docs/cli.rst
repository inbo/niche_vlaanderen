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

