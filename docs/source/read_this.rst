
====================
Purpose and Concepts
====================

Hypergol is a data science productivity framework designed around two core principles:

 - Enabling good code quality and iterative improvements
 - Low friction start and high performance

Restrictions
------------

The framework imposes several limitations but only in directions that don't inhibit principal objectives. You are restricted to one (but any size that you can buy on AWS/GCP) machine, in exchange, there is virtually no setup. You need to use git version control (you should use it anyway), but you get version-controlled code, data and data lineage. You need to define your entire domain in Hypergol classes, but you never need to worry about saving/loading them even if you modify the code.

Accelerate into production and iterate
--------------------------------------

It enables you to rapidly move your project to a point where you can perform industrial-scale analysis and iterate on code and models while still maintaining data lineage.

No more chores, good structure from the start
---------------------------------------------

It automates the "chores" of data science: writing shell scripts, creating virtual environments and setting up git repositories. It provides examples of how to write unit tests, how to pass parameters from shell scripts to python code and many others. If you make a mistake, the tests or the framework itself tells you what might be the source of the problem.

Focus on what matters
---------------------

It creates an opinionated framework that enforces you writing modular and coherent code. Still, in exchange, you only need to write the part that is problem-specific; everything else is given.

Fast large scale execution
--------------------------

It enables evaluating models on large scale datasets on multi-core servers and provide detailed analysis on model performance. You don't need to worry about the infrastructure, limitations and difficulties of other DAG-based workflow management platforms. Hypergol operates on a single but arbitrary large machine. The pipeline

Good luck using it and get in touch with us about bugs and successes: `Hypergol Feedback <mailto:hypergol.developer@gmail.com>`_.
