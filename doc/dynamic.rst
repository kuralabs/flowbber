=================
Dynamic Pipelines
=================

.. versionadded:: 1.9.0

.. contents::
   :local:

Flowbber allows to create dynamic pipelines using a templating engine named
Jinja2_.

A dynamic pipeline allows, among others, to:

#. Conditionally add / remove pipeline components or configuration options.
#. Multiply components on demand.
#. Parametrize or change any other pipeline element.

In some situations the number of sources (inputs), aggregators (modifiers,
analyzers) or sinks (outputs) of a same type may vary depending on the
environment it was run.

A typical example of this situation is of a testing suite that is parallelized
into many chunks, one for each CPU cores the machine has, or one for each machine in a cluster running the suite. In this
scenario, many ``.xml`` files with the results for each chunks are produced.
Because the number of CPU cores varies from machine to machine, a static
pipeline defining sources for each ``.xml`` file generated is inadequate.

Another scenario is that of a large pipeline that needs to be reused for a
similar workflow with minimal changes. In this case, some components may be
conditionally included, or arbitrary elements of the pipeline need to be
modified.

For this scenarios Flowbber allows to create dynamic pipelines using a
templating engine named Jinja2_.


.. code-block:: sh

    $ flowbber -vv --values-file values.toml pipeline.toml.tpl

.. _Jinja2: http://jinja.pocoo.org/
