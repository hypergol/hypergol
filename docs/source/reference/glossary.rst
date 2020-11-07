.. _glossary:

Glossary of Terms
=================

.. glossary::

   chunk
      Each dataset is consisting of several chunks that store objects whose hash id starts with the same characters (and matches the chunk's chunk id).

   chunk count
      the total number of chunks in a dataset, valid numbers: 16, 256, 4096.

   chunk id
      1-2-3 character hexadecimal number in string format depending on the chunk count of a dataset. All objects whose hash is starting with the chunk id must be in the chunk identified by the chunk id.

   delayed
      At execution, each task is pickled, and a copy of it is created in the thread. If a class cannot be pickled, it cannot be a member of the task before execution. :class:`.Delayed` solves this problem by delaying the creation recursively until the execution in the thread starts

   hash
      40 digit hexadecimal value generated with SHA1 method.

   hash id
      fields of a domain object can be used to find out which chunk the object will be in a dataset.

   id
      fields that uniquely identify an object. Two objects deemed equal if their id's match.
