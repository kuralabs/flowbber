==========
Quickstart
==========

.. contents::
   :local:

Introduction
============

Flowbber is a Python configuration-based pipeline executor and framework that
allows to:

#. Collect data from many different sources concurrently.
#. Analyze and process the data.
#. Publish the data to many different data stores.

This can be accomplish in a very easy and flexible way, and enables many use
cases from many different domains.


Quick Installation
==================

Flowbber can be easily installed from PyPI_ using pip_:

.. code-block:: sh

    pip3 install flowbber

.. important::

    Flowbber is available for Python3 only and tested in Python 3.5+.

.. _PyPI: https://pypi.python.org/pypi/flowbber
.. _pip: https://pip.pypa.io/en/stable/installing/

Verifying installation
----------------------

Check that you can launch the flowbber executable:

.. code-block:: console

    $ flowbber --version
    Flowbber v1.0.0

Help is available using the ``--help`` flag:

.. code-block:: console

    $ flowbber --help
    usage: flowbber [-h] [-v] [--version] pipeline

    Flowbber is a generic tool and framework that allows to execute custom
    pipelines for data gathering, publishing and analysis.

    positional arguments:
      pipeline       Pipeline definition file

    optional arguments:
      -h, --help     show this help message and exit
      -v, --verbose  Increase verbosity level
      --version      show program's version number and exit


Key Concepts
============

As an executor, Flowbber provides the ``flowbber`` executable which is
responsible for loading a textual pipeline definition and execute the data
**collection**, **analysis** and **publishing** routines as defined.

The pipeline definition can be written in a simple JSON_ or TOML_ format, and
specifies the stages of your pipeline:

.. _JSON: http://www.json.org/
.. _TOML: https://github.com/toml-lang/toml

- **Sources**: what data to collect and how.
- **Aggregators**: how to accumulate or process the collected data.
- **Sinks**: How to publish, store or transmit the resulting data.

As a framework, Flowbber allows to create the components (sources, aggregators
and sinks) for your custom data pipeline.

.. figure:: _static/images/arch.svg
   :align: center

   Execution of a Flowbber pipeline.
