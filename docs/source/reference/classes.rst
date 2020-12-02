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

=====================================================
DatasetFactory - Convenience class to create datasets
=====================================================

.. currentmodule:: hypergol
.. autoclass:: DatasetFactory

**************************
Pipelining Related Classes
**************************

====================================================
Task - Class for create datasets from other datasets
====================================================

.. currentmodule:: hypergol
.. autoclass:: Task
    :private-members:

===========================================================
Pipeline - Class for organising tasks and datasets together
===========================================================

.. currentmodule:: hypergol
.. autoclass:: Pipeline

======================================================
Job - Class for passing information on chunks to tasks
======================================================

.. currentmodule:: hypergol.job
.. autoclass:: Job

====================================================================
JobReport - Class for passing results of a task back to the pipeline
====================================================================

.. currentmodule:: hypergol.job_report
.. autoclass:: JobReport

============================================================
Delayed - Helper class to allow passing any class to threads
============================================================

.. currentmodule:: hypergol
.. autoclass:: Delayed
    :private-members:


******************************
Model Creation Related Classes
******************************

==================================================================
BaseBatchProcessor - Class for handling input/output for the model
==================================================================

.. currentmodule:: hypergol
.. autoclass:: BaseBatchProcessor

===============================================================
BaseTensorflowModelBlock - Class for organising Tensorflow code
===============================================================

.. currentmodule:: hypergol
.. autoclass:: BaseTensorflowModelBlock

==========================================================
BaseTensorflowModel - Class for organising Tensorflow code
==========================================================

.. currentmodule:: hypergol
.. autoclass:: BaseTensorflowModel

=========================================================================
TensorflowModelManager - Class for managing model training and evaluation
=========================================================================

.. currentmodule:: hypergol
.. autoclass:: TensorflowModelManager

*********************
Miscellaneous Classes
*********************

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

===============================================================
HypergolProject - Class to manage information about the project
===============================================================

.. currentmodule:: hypergol.hypergol_project
.. autoclass:: HypergolProject

=============================================================
RepoManager - Helper class for storing Repository information
=============================================================

.. currentmodule:: hypergol.hypergol_project
.. autoclass:: RepoManager

=========================================================
RepoData - Data class for storing Repository informations
=========================================================

.. currentmodule:: hypergol.dataset
.. autoclass:: RepoData

==========================
Logger - Class for logging
==========================

.. currentmodule:: hypergol.logger
.. autoclass:: Logger
