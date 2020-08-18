.. _cli:

*************
CLI Functions
*************

Hypergol provides a set of functions to autogenerate components of the framework. All functions can be called in the command line, boolean flags can be specified as ``--dryrun`` or ``--dryrun=False`` for example:

.. code:: bash

    $ python3 -m hypergol.cli.create_<...>  <parameters>

The same command can be executed in python as:

.. code:: python

    from hypergol.cli.create_<...> import create_<...>
    create_<...>(<parameters>)

Hypergol uses `Python Fire <https://google.github.io/python-fire/guide/>`__ to wrap python functions and enable CLI execution.

=================================================
create_project - Autogenerate project directories
=================================================

.. currentmodule:: hypergol.cli.create_project
.. autofunction:: create_project

===============================================
create_data_model - Autogenerate domain classes
===============================================

.. currentmodule:: hypergol.cli.create_data_model
.. autofunction:: create_data_model

===========================================
create_task - Autogenerate processing tasks
===========================================

.. currentmodule:: hypergol.cli.create_task
.. autofunction:: create_task

===================================================
create_pipeline - Autogenerate processing pipelines
===================================================

.. currentmodule:: hypergol.cli.create_pipeline
.. autofunction:: create_pipeline

=========================================================
create_model_block - Autogenerate Tensorflow model blocks
=========================================================

.. currentmodule:: hypergol.cli.create_model_block
.. autofunction:: create_model_block

=============================================
create_model - Autogenerate Tensorflow models
=============================================

Also generates training script and batch data manager class

.. currentmodule:: hypergol.cli.create_model
.. autofunction:: create_model

======================================
list_datasets - List existing datasets
======================================

.. currentmodule:: hypergol.cli.list_datasets
.. autofunction:: list_datasets

===============================================================
diff_data_model - Print differences between data model versions
===============================================================

.. currentmodule:: hypergol.cli.diff_data_model
.. autofunction:: diff_data_model

=========================================================================
create_old_data_model - Create an older version of the datamodel from git
=========================================================================

.. currentmodule:: hypergol.cli.create_old_data_model
.. autofunction:: create_old_data_model
