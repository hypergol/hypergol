.. _glossary:

Glossary
========

.. glossary::

   chunk
      Each dataset is consisting of a number of chunks that store objects whose hash id starts with the same characters (and matches the chunks chunk id).

   chunk id
      1-2-3 character depending on the number of chunks in a dataset. All objects whose hash is starting with the chunk id will be in the chunk identified by the chunk id.

   hash
      40 digit hexadecimal value generated with SHA1 method.

   hash id
      fields of a domain object can be used to find out which chunk the object will be in a dataset.

   id
      fields that uniquely identify an object. Two objects deemed equal if their id's mathch.
