==========
Quickstart
==========

.. contents::
   :local:

Introduction
============

Flowbber is a configuration-based :term:`pipeline executor <Pipeline Executor>`
and framework written in Python 3 that allows to:

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

    Flowbber is available for Python 3 only and tested in Python 3.5+.

.. _PyPI: https://pypi.python.org/pypi/flowbber
.. _pip: https://pip.pypa.io/en/stable/installing/

Verifying installation
----------------------

Check that you can launch the ``flowbber`` command line application:

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

As a :term:`pipeline executor <Pipeline Executor>`, Flowbber provides the
``flowbber`` command line application which is responsible for loading a
textual :term:`pipeline definition <Pipeline Definition>` and execute the data
**collection**, **analysis** and **publishing** routines as defined.

The pipeline definition can be written in a simple JSON_ or TOML_ format, and
specifies the stages of your pipeline:

.. _JSON: http://www.json.org/
.. _TOML: https://github.com/toml-lang/toml

- :term:`Sources <Source>`: what data to collect and how.
- :term:`Aggregators <Aggregator>`: how to accumulate or process the collected
  data.
- :term:`Sinks <Sink>`: How to publish, store or transmit the resulting data.

As a framework, Flowbber allows to create the :term:`components <Component>`
(sources, aggregators and sinks) for your custom data pipeline in an easy and
straightforward way.

Flowbber will execute any pipeline in the following way:

.. figure:: _static/images/arch.svg
   :align: center

   Execution of a Flowbber pipeline.

As shown in the diagram above, the list of :term:`sources <Source>` will be run
**concurrently**, each one in its own subprocess. Each source will provide some
arbitrary data that will be collected into a bundle that maps the identifier
of each source to the data it provided.

Once all sources have run and all data have been collected into the bundle,
the list of :term:`aggregators <Aggregator>` will be run **sequentially**.

The entirety of the collected data will be passed to each aggregator, which is
allowed to produce more data based on the collected data, modify the data, or
even delete entries in the bundle.

Any data transformation is valid, and the modified data will be passed to the
next aggregator, making the order in which the aggregators run very important.

This behavior makes the aggregator the more flexible and powerful component of
the pipeline. Nevertheless, in many use cases only sources and sinks are
required. A valid pipeline requires at least one source and one sink, a thus
aggregators are optional.

Finally, when the last aggregator has run, the data will be considered done and
become read-only. The data is then passed to each :term:`sink <Sink>`, which
will also run **concurrently**, each one in its own subprocess.

Sinks can modify or transform the passed data at will if required, but those
modifications will have no impact in the data the others sinks have. It is
expected that the sinks store or publish the data in some form, for example
submitting it to a database, writing a file, rendering a template, sending it
by email, among some examples.


Glossary
========

.. glossary::

    Pipeline
        A chain of data-processing stages. A Flowbber Pipeline must contain at
        least one :term:`Source` and one :term:`Sink`.

    Pipeline Definition
        A file or data structure describing the stages and
        :term:`Components <Component>` of a :term:`Pipeline` and its
        configuration.

    Pipeline Executor
        An application responsible of executing a :term:`Pipeline`.

    Source
        A type of :term:`Component` that is responsible for collecting data
        from a particular data source.

    Aggregator
        A type of :term:`Component` that is responsible for analyzing,
        relating, accumulate or process the data collected by the
        :term:`Sources <Source>`.

    Sink
        A type of :term:`Component` that is responsible for publishing the data
        collected to a particular data store.

    Plugin
        A modular :term:`Component` that performs a very specific task and was
        created for a single purpose. It is usually packaged and distributed
        apart.

    Component
        A component of a stage in a :term:`Pipeline`. Either a :term:`Source`,
        an :term:`Aggregator` or a :term:`Sink`.
