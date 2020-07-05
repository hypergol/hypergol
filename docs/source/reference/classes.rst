.. _classes:

********************
Data Related Classes
********************

Hypergol provides a set of classes to define, store and process domain objects.

========================================
BaseData - Base class for domain objects
========================================

.. currentmodule:: hypergol
.. autoclass:: BaseData

==========================================
Dataset - Class for storing domain objects
==========================================

.. currentmodule:: hypergol
.. autoclass:: Dataset

==========================================
DatasetWriter - Class for writing datasets
==========================================

.. currentmodule:: hypergol.dataset
.. autoclass:: DatasetWriter

==========================================
DatasetReader - Class for reading datasets
==========================================

.. currentmodule:: hypergol.dataset
.. autoclass:: DatasetReader

=============================================
DataChunk - Internal class for handling files
=============================================

.. currentmodule:: hypergol.dataset
.. autoclass:: DataChunk

********************
Task Related Classes
********************

===============================
BaseTask - Base class for tasks
===============================

.. currentmodule:: hypergol.base_task
.. autoclass:: BaseTask
    :private-members:

==================================================
Source - Class for creating datasets from raw data
==================================================

.. currentmodule:: hypergol
.. autoclass:: Source

==========================================
SimpleTask - Class for processing datasets
==========================================

.. currentmodule:: hypergol
.. autoclass:: SimpleTask

====================================================
Task - Class for create datasets from other datasets
====================================================

.. currentmodule:: hypergol
.. autoclass:: Task
    :private-members:

**************************
Pipelining Related Classes
**************************

===========================================================
Pipeline - Class for organising tasks and datasets together
===========================================================

.. currentmodule:: hypergol
.. autoclass:: Pipeline

======================================================
Job - Class for passing information on chunks to tasks
======================================================

.. currentmodule:: hypergol.base_task
.. autoclass:: Job

====================================================================
JobReport - Class for passing results of a task back to the pipeline
====================================================================

.. currentmodule:: hypergol.base_task
.. autoclass:: JobReport

============================================================
Delayed - Helper class to allow passing any class to threads
============================================================

.. currentmodule:: hypergol
.. autoclass:: Delayed

*************
Miscellaneous
*************

=============================================
Repr - Convenience class for default printing
=============================================

.. currentmodule:: hypergol
.. autoclass:: Repr

=========================================
NameString - Convert string between cases
=========================================

.. currentmodule:: hypergol.name_string
.. autoclass:: NameString

====================================================
HypergolProject - Helper class for the CLI functions
====================================================

.. currentmodule:: hypergol.hypergol_project
.. autoclass:: HypergolProject
