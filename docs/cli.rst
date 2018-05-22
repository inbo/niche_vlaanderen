########################
Niche Configuration file
########################

.. _simple_config:

Simple model
============

Instead of running Niche interactively, it can be used  with a configuration file.
For a simple NICHE model this could look like this:

 .. code-block:: yaml

     model_options:
       full_model: False
       output_dir: _output

     input_layers:
       mhw: data/mhw_small.asc
       mlw: data/mlw_small.asc
       soil_code: data/soil_code_small.asc

The file specifies the input layers, the output directory(``output_dir``), and other model options.
In this case, as we have a simple model (:ref:`simple`), as specified in the model options.

.. _full_model:

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

As the option ``full_model=True`` is given (it is enabled by default, so can be omitted) all input layers are used.
The other model options correspond to the parameters that could be given to the :func:`niche_vlaanderen.Niche.run` method.

.. _abiot_dev_config:

Abiotic and/or deviation
=========================
Using a configuration file, it is also possible to use abiotic values, like
previously demonstrated in `Using abiotic grids`_.

To do this the values ``acidity`` and ``nutrient_level`` must be specified,
together with the ``abiotic`` model option.

The option ``deviation`` creates deviation maps, which show the difference between
the borders specified in the niche table and the actual values of mhw and mlw for
every soil type, as discussed in `Creating deviation maps`_.

.. _flood_config:

Flooding module
===============
If you want to calculate a niche object combined with a Flooding model, this is possible by
adding a flooding block. Different scenarios can be specified. They need a single name.
The output of the module will be written to the same directory as the output specified in the model options.

.. code-block:: yaml

   flooding:
     - name: T25-winter
       depth: T25.tif
       frequency: T25
       duration: short
       period: winter
     - name: T25-zomer
       ....

.. _gen_config_int:

Generating a config file in interactive mode
============================================

When running Niche in interactive mode, representing the model will show the
corresponding configuration file. This was demonstrated in `Showing the model configuration`_.

Also when writing a grid using the write method a "log.txt" file will be written.
This file itself is also a valid configuration file for a next run. The list with generated files will be ignored.

.. _run_config_int:

Running a config file in interactive mode
=========================================

When using Niche in interactive mode, you can load all data from a config file using the
:func:`niche_vlaanderen.Niche.read_config_file` method, or you can run all by using the
:func:`niche_vlaanderen.Niche.run_config_file` method.

.. _run_config_cl:

Running a config file from the command line
===========================================

After opening the anaconda prompt (and starting the environment) you can also run niche from a command line using a
config file. This is done by running the ``niche`` application.

.. code-block:: bash

    niche example.yml

.. note::

    If you don't specify an output directory, nothing will be written - in command line mode this makes no sense

.. _full_example:

Full example
==============

We offer a full example (included below) which contains all possible options and some documentation.
This file may be a good starting point for creating your own configuration files.

This full example can be generated from the command line by running ``niche --example``

 .. literalinclude:: ../niche_vlaanderen/system_tables/example.yaml

.. _`Using abiotic grids`: https://inbo.github.io/niche_vlaanderen/advanced_usage.html#Using-abiotic-grids
.. _`Showing the model configuration`: https://inbo.github.io/niche_vlaanderen/getting_started.html#Showing-the-model-configuration
.. _`Creating deviation maps`: https://inbo.github.io/niche_vlaanderen/advanced_usage.html#Creating-deviation-maps
