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
