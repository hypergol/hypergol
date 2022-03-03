Install
=======

Hypergol requires Python 3.8 or above. Below we assume you have the default Python environment already configured on your computer and you intend to install ``hypergol`` inside of it.  If you want to create and work with Python virtual environments, please follow instructions on `venv <https://docs.python.org/3/library/venv.html>`_ and `virtual environments <http://docs.python-guide.org/en/latest/dev/virtualenvs/>`_.

First, make sure you have the latest version of ``pip`` (the Python package manager) installed. If you do not, refer to the `Pip documentation <https://pip.pypa.io/en/stable/installing/>`_ and install ``pip`` first.

Install the released version
----------------------------

Install the current release of ``hypergol`` with ``pip``::

    $ pip install hypergol

To upgrade to a newer release use the ``--upgrade`` flag::

    $ pip install --upgrade hypergol

If you do not have permission to install software systemwide, you can
install into your user directory using the ``--user`` flag::

    $ pip install --user hypergol


Install the development version
-------------------------------

If you have `Git <https://git-scm.com/>`_ installed on your system, it is also
possible to install the development version of ``hypergol``.

Before installing the development version, you may need to uninstall the
standard version of ``hypergol`` using ``pip``::

    $ pip uninstall hypergol

Then do::

    $ git clone https://github.com/hypergol/hypergol.git
    $ cd hypergol
    $ pip install -e .

The ``pip install -e .`` command allows you to follow the development branch as
it changes by creating links in the right places and installing the command
line scripts to the appropriate locations.

Then, if you want to update ``hypergol`` at any time, in the same directory do::

    $ git pull
