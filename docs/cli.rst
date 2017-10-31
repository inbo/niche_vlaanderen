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
In this case, as we have a simple model, this is specified.

