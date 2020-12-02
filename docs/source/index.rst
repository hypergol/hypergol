.. meta::
   :google-site-verification: 0I5MQxqHDvxeNRoP4W8z1Wli0ur-W1kdXFv-lfLSlH8

.. _contents:

This project is under construction; please contact the authors with feedback by the `Contact page <contact.html#contact>`_.


Hypergol Documentation
======================

Hypergol is a data science workflow system that enables maintaining code quality, data lineage and efficient execution throughout a data-intensive project lifecycle. It takes care of all the chores, setup and glue code to bring you effortlessly into a state where you can focus on what matters most.

Hypergol provides:

-  code generation to set up the project structure with a virtual environment, testing, linting and git files;
-  code generation at project start to build the domain data model, and generate pipeline skeleton code;
-  data format to store the domain objects that are both accessible from notebooks and in parallel execution;
-  simple parallel processing pipeline without external dependencies (based on python's own ``multiprocessing`` package), you only write the single-threaded code, and it seamlessly parallelises it on your data;
-  includes version control information in your datasets to track the actual code that was used to create them and enable schema evolution (change the definition of domain objects and translate old data into the new one) (WIP);

Audience
--------

The audience for Hypergol is data scientists who need to deal with ad-hoc large data processing tasks on an ongoing basis. It replaces working with hard to replicate/iterate notebook based workflows with a version-controlled and streamlined process enabling the parallel processing of large datasets. On the other hand, it doesn't need the infrastructure of other ETL pipelines and can run on a machine of any size.

It accelerates a project's start in experimental phase by code generation. It also enables fast and efficient data processing by simple, map-reduce-like, single machine multithreaded pipeline.

Free software
-------------

Hypergol is free software; you can redistribute it and/or modify it under the terms of the :doc:`MIT </license>` license.  We welcome contributions.

Join us
-------

Join us on `GitHub <https://github.com/hypergol/hypergol>`_ or on `Slack <https://hypergol.ml/slack>`_.

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

   read_this
   install
   tutorial
   reference/index
   license
   credits
   citing
   contact

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
* :ref:`glossary`
