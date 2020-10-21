Hypergol
========

Hypergol is a Data Science productivity toolkit to accelerate small team projects into production at the shortest possible time while still maintaining high standard code. This is achieved by autogenerating structure and code in a form that is easy to extend so only the project specific code need to be filled.

Hypergol provides parallel execution capabilities with little restrictions. This enables a small team to accelerate time consuming tasks by renting larger instances from a cloud provider, but with no additional infrastructure setup time and cost.

The toolkit provides a standard serialisation (autogenerated) and storage system that enables parallel processing natively but easily accessible from any python code including jupyter notebooks.

A Hypergol Project is connected to a git repo that acts as a version controller and both code and generated data are linked to git branches and commits. Full data lineage can be retrieved and storage system is verifiable through SHA1 hashes.

Tensorflow model stubs can be generated that enable standardised model development and training that both connects to the storage system above, observe [SOLID](https://en.wikipedia.org/wiki/SOLID) principles and enable autogenerated deployment with [FastAPI](https://fastapi.tiangolo.com/).

See documentation for further details at: [https://hypergol.readthedocs.io/en/latest/](https://hypergol.readthedocs.io/en/latest/)

Join our community at: [Hypergol Slack Community](https://join.slack.com/t/hypergol/shared_invite/zt-ilc5qrjl-GtpZ~XFjvHM1GYDyB5EvtQ)

Quick Start
-----------

Install it with:

```
pip intall hypergol
```

Create your first projects:

```
python3 -m hypergol.cli.create_project MyFirstProject
cd my_first_project
```

And follow instructions in the projects `README.md` or the tutorial at: [https://hypergol.readthedocs.io/en/latest/tutorial.html](https://hypergol.readthedocs.io/en/latest/tutorial.html)

Good Luck using Hypergol!
-------------------------

The authors wish that Hypergol frees you from tedious tasks so you can focus more on the core part of Machine Learning and generate everything else.

May the productivity be with you!

Join our community at: [Hypergol Slack Community](https://join.slack.com/t/hypergol/shared_invite/zt-ilc5qrjl-GtpZ~XFjvHM1GYDyB5EvtQ)

All feedback is welcome at: [hypergol.developer@gmail.com](mailto:hypergol.developer@gmail.com?subject=Hypergol%20Feedback)
