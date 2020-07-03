.. _contents:

Hypergol Documentation
======================

Hypergol is a data science workflow system that enables maintaining code quality, data lineage and efficient execution throughout a data intensive project lifecycle. It takes care of all the chores, setup and glue code to bring you effortlessly into a state where you can focus on what matters most.

Hypergol provides:

-  code generation to setup the project structure with virtual environment, testing, linting and git files;
-  code generation at project start to build the domain data model, and generate pipeline skeleton code;
-  data format to store the domain objects that is both accessible from notebooks and in parallel execution;
-  simple parallel processing pipeline without external dependencies (based on python's own ``multiprocessing`` package), you only write the single threaded code and it seamlessly parallelises it on your data;
-  include version control information in your datasets to track the actual code that was used to create them and enable schema evolution (change the definition of domain objects and translate old data into the new one) (WIP);

Audience
--------

The audience for Hypergol are data scientists who need to deal with ad-hoc large data processing tasks on an ongoing basis. It replaces working with hard to replicate/iterate notebook based workflows with a version controlled and streamlined process enabling the parallel processing of large datasets.

It accelarates project start in experimental phase by code generation. Enables fast and efficient data processing by a simple, map-reduce-like, single machine multithreaded pipeline.

Free software
-------------

Hypergol is free software; you can redistribute it and/or modify it under the
terms of the :doc:`MIT </license>`.  We welcome contributions.
Join us on `GitHub <https://github.com/hypergol/hypergol>`_.

History
-------

Hypergol was written in July 2020. The original version was designed and written by Laszlo Sragner and Rhys Patten.
Many people have contributed to the success of Hypergol. Some of the contributors are listed in the :doc:`credits. <credits>`

Documentation
-------------

.. only:: html

    :Release: |version|
    :Date: |today|

.. toctree::
   :maxdepth: 1

   install
   tutorial
   reference/index
   license
   credits
   citing

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
* :ref:`glossary`
