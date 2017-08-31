=============================
Implementing Custom Pipelines
=============================

To implement your custom components you must create a class that subclasses
one of the 3 available components as described in :ref:`implementing`.

Once implemented, you can register it to make it available to Flowbber as
described in :ref:`registering`.

To allow passing configuration options to your component, implement the
``declare_config()`` method as described in :ref:`options`.

.. contents::
   :local:


.. _implementing:

Implementing Components
=======================

Depending on the type of component you want to create, subclass one of the
following classes and implement its abstract method.

Sources
-------

To implement a :term:`Source` component, subclass the Flowbber's
:class:`flowbber.components.Source` class and implement the
:meth:`flowbber.components.Source.collect` abstract method.

.. autoclass:: flowbber.components.Source
   :members:

Source's ``collect()`` method must return a dictionary with the collected data,
using key as label and value as value of the label. The collected data
structure can be more complicated and nested as required, as long as JSON
serializable objects are used, for example built-in datatypes like integers,
booleans, floats, strings, and data structures like dictionaries and lists.

For example, consider a basic implementation of the built-in
:ref:`EnvSource <sources-env>` that collects data from the environment:

.. code-block:: python3

    from os import environ
    from flowbber.components import Source


    class MySource(Source):
        def collect(self):
            return {
                key, value
                for key, value in environ.items()
            }

Aggregators
-----------

To implement an :term:`Aggregator` component, subclass the Flowbber's
:class:`flowbber.components.Aggregator` class and implement the
:meth:`flowbber.components.Aggregator.accumulate` abstract method.

.. autoclass:: flowbber.components.Aggregator
   :members:

Aggregator's ``accumulate()`` method takes the editable bundle of data
collected by the sources and doesn't return anything, but it is allowed to
mutable, add or delete data from the bundle.

For example, consider a pipeline that uses twice the built-in
:ref:`CoberturaSource <sources-cobertura>` because your codebase has a part
written in C and another one in Go, and you need a global coverage metric.

The pipeline's sources could look like this:

.. code-block:: toml

    [[sources]]
    type = "cobertura"
    id = "coverage_c"

        [sources.config]
        xmlpath = "{git.root}/build/test/c/coverage.xml"

    [[sources]]
    type = "cobertura"
    id = "coverage_go"

        [sources.config]
        xmlpath = "{git.root}/build/test/go/coverage.xml"

The data gathered by both sources could look like this:

.. code-block:: python3

    OrderedDict([
        ('coverage_c', {
            'files': {
                # ...
            },
            'total': {
                'total_statements': 1000,
                'total_misses': 200,
                'line_rate': 0.80
            }
        }),
        ('coverage_go', {
            'files': {
                # ...
            },
            'total': {
                'total_statements': 200,
                'total_misses': 100,
                'line_rate': 0.50
            }
        })
    ])

We could implement a basic aggregator that sums the total of both suites:

.. code-block:: python3

    from flowbber.components import Aggregator


    class MyAggregator(Aggregator):
        def accumulate(self, data):

            ids = ['coverage_c', 'coverage_go']
            total_statements = 0
            total_misses = 0

            for datakey in ids:
                total = data[datakey]['total']
                total_statements += total['total_statements']
                total_misses += total['total_misses']

            total_hits = total_statements - total_misses
            line_rate = total_hits / total_statements

            data[self.id] = {
                'total_statements': total_statements,
                'total_misses': total_misses,
                'line_rate': line_rate
            }

Assuming that we :ref:`register <registering>` this aggregator as
``my_aggregator``, we could add it to the pipeline definition file like this:

.. code-block:: toml

    [[aggregators]]
    type = "my_aggregator"
    id = "total_coverage"

The above aggregator will transform the collected data like this:

.. code-block:: python3

    OrderedDict([
        ('coverage_c', {
            # ...
        }),
        ('coverage_go', {
            # ...
        }),
        ('total_coverage', {
            'total_statements': 1200,
            'total_misses': 300,
            'line_rate': 0.75
        })
    ])

Note that while we hardwired the ids of the sources this could be parametrized
to the component as described in :ref:`options`. Also note they way we used
``self.id`` as the key to add to the bundle.

Sinks
-----

To implement a :term:`Sink` component, subclass the Flowbber's
:class:`flowbber.components.Sink` class and implement the
:meth:`flowbber.components.Sink.distribute` abstract method.

.. autoclass:: flowbber.components.Sink
   :members:

Sink's ``distribute()`` method takes a copy of the final collected data (after
passing all aggregators) and returns nothing.

For example, consider a basic and naive implementation of the built-in
:ref:`MongoDBSink <sinks-mongodb>` that submits data to a MongoDB database:

.. _example-sink-mongodb:

.. code-block:: python3

    from flowbber.components import Sink
    from flowbber.logging import get_logger


    log = get_logger(__name__)


    class SimpleMongoDBSink(Sink):
        def distribute(self, data):
            from pymongo import MongoClient

            client = MongoClient('mongodb://localhost:27017/')
            database = client['mydatabase']
            collection = database['mycollection']

            data_id = collection.insert_one(data).inserted_id
            log.info('Inserted data to MongoDB with id {}'.format(data_id))

In this example we hardwired the connection URI, database name and collection
name. This can be parametrized as described in :ref:`options`. Check the
code of :class:`flowbber.plugins.sinks.mongodb.MongoDBSink` for a full example
on the implementation of the MongoDB sink.


.. _registering:

Registering Components
======================

Entrypoints
-----------

Flowbber uses setuptools' entrypoints_ to perform dynamic discovery of
:term:`plugins <Plugin>`.

.. _entrypoints: http://setuptools.readthedocs.io/en/latest/setuptools.html#dynamic-discovery-of-services-and-plugins

Asumming your package is called ``mypackage``, add an ``entry_points`` keyword
argument to your package ``setup.py``'s ``setup()`` function as follows:

.. code-block:: python3

    setup(
        # ...
        # Entry points
        entry_points={
            'flowbber_plugin_sources_1_0': [
                'mysource = mypackage.sources.mycustom:MyCustomSource'
            ],
            'flowbber_plugin_aggregators_1_0': [
                'myaggregator = mypackage.aggregators.mycustom:MyCustomAggregator'
            ],
            'flowbber_plugin_sinks_1_0': [
                'mycustom = mypackage.sinks.mycustom:MyCustomSink'
            ]
        }
    )

As key, use one of the following entrypoints:

:Sources: ``flowbber_plugin_sources_1_0``
:Aggregators: ``flowbber_plugin_aggregators_1_0``
:Sinks: ``flowbber_plugin_sinks_1_0``

The elements in the list associated with those entrypoints have the following
structure:

.. code-block:: text

    <your_new_type> = <yourpackage>.<submodule>.<submodule>:<YourComponentClass>

Please note the ``:`` (colon) after the module path. Once installed alongside
Flowbber, your package will be available for use using ``type = your_new_type``
in your pipeline definition file.


Pipeline's flowconf
-------------------

In many situations, creating a whole Python package with just a couple of
components, installing it and keeping track of its version is too much
overhead.

For example, what if your custom pipeline can be implemented with Flowbber's
built-in :ref:`sources` and :ref:`sinks`, but you only require one additional
simple aggregator?

Flowbber supports creating local configuration modules that allows to create
components specific to a pipeline.

Create a ``flowconf.py`` file next to your pipeline definition file. If you
have placed your pipeline under version control, keeping track of both the
components and the definition of the pipeline is straightforward. Flowbber
will load the components defined in this way and made it available to your
pipeline.

In the ``flowconf.py`` file, you can register your components using the
``register`` function for each loader:

**Sources:**

.. code-block:: python3

    from flowbber.loaders import source
    from flowbber.components import Source


    @source.register('my_source')
    class MySource(Source):
        def collect(self):
            return {'my_value': 1000}

**Aggregators:**

.. code-block:: python3

    from flowbber.loaders import aggregator
    from flowbber.components import Aggregator


    @aggregator.register('my_aggregator')
    class MyAggregator(Aggregator):
        def accumulate(self, data):
            data['num_sources'] = {'total': len(data.keys())}

**Sinks:**

.. code-block:: python3

    from flowbber.loaders import sink
    from flowbber.components import Sink


    @sink.register('my_sink')
    class MySink(Sink):
        def distribute(self, data):
            print(data)

With the above configuration file, the pipeline definition file can use those
components:

.. code-block:: toml

    [[sources]]
    type = "my_source"
    id = "my_source1"

    [[sources]]
    type = "my_source"
    id = "my_source2"

    [[aggregators]]
    type = "my_aggregator"
    id = "my_aggregator1"

    [[sinks]]
    type = "my_sink"
    id = "my_sink1"

The resulting collected data will be:

.. code-block:: python3

    OrderedDict([
        ('my_source1', {'my_value': 1000}),
        ('my_source2', {'my_value': 1000}),
        ('num_sources', {'total': 2})
    ])


.. _options:

Specifying Options
==================

Any :term:`component <Component>` can implement the method
:meth:`flowbber.components.base.Component.declare_config`:

.. automethod:: flowbber.components.base.Component.declare_config
   :noindex:

It is expected that for each option the component requires to declare, a call
to :meth:`flowbber.config.Configurator.add_option` is performed.

.. automethod:: flowbber.config.Configurator.add_option
   :noindex:

For example, let's retake our previous simple
:ref:`MongoDB sink example <example-sink-mongodb>`. We want to parametrize,
among other things, the ``uri``, ``database`` and ``collection``.

.. code-block:: python3

    def declare_config(self, config):
        config.add_option(
            'uri',
            default=None,
            optional=True,
            schema={
                'type': 'string',
                'empty': False,
                'nullable': True,
            },
            secret=True,
        )

        config.add_option(
            'database',
            schema={
                'type': 'string',
                'empty': False,
            },
        )

        config.add_option(
            'collection',
            schema={
                'type': 'string',
                'empty': False,
            },
        )

The ``schema`` keyword argument receives a dictionary that describes the schema
for which the value will be validated. Validation is performed using the
awesome Cerberus_ library, and allows to create schemas for complex data types
and values. If the schema is set to ``None``, no validation will be performed.

.. _Cerberus: http://docs.python-cerberus.org/en/stable/

Once validated and normalized, configuration options will be available under
the read only ``self.config`` attribute. The keys of the configuration options
are mapped to an object with three attributes:

:key: Key of the configuration option. Same as given as first argument to
 ``add_option``.
:value: The validated and normalized or default value of the option.
:is_secret: Boolean indicating that the option is a secret and thus shouldn't
 be printed, logged, stored in plain text, etc. Same as ``add_option``'s
 ``secret`` keyword argument.

 In this sense, it is important to note that Flowbber won't log or store any
 option marked as secret.

Following our simple MongoDB example, we could use the configurations options
as follows:

.. code-block:: python3

    from flowbber.components import Sink


    class SimpleMongoDBSink(Sink):
        def declare_config(self, config):
            # Declare options ...

        def distribute(self, data):
            from pymongo import MongoClient

            client = MongoClient(self.config.uri.value)
            database = client[self.config.database.value]
            collection = database[self.config.collection.value]

            # ...

Finally, in some situations a basic option by option validation is
insufficient, for example, if two options are incompatible between them.

In this situations the component can register a custom validation function
using the :meth:`flowbber.config.Configurator.add_validator` method:

.. automethod:: flowbber.config.Configurator.add_validator
   :noindex:

The function registered will receive the validated data as a dictionary just
before its freezing and can perform any modification required on the data.

For example, consider the :ref:`MongoDBSink <sinks-mongodb>` that allows to
define the connection parameters either as a single string or as multiple
values:

.. code-block:: python3

    def declare_config(self, config):

        # ... calls to add_option()

        # Check if uri is defined and if so then delete other keys
        def custom_validator(validated):
            if validated['uri'] is not None:
                del validated['host']
                del validated['port']
                del validated['username']
                del validated['password']
            else:
                del validated['uri']

        config.add_validator(custom_validator)

This validation function could perform checks against values, for example in
:ref:`TimestampSource <sources-timestamp>` where at least one format needs to
be enabled:

.. code-block:: python3

    def declare_config(self, config):

        # ... calls to add_option()

        # Check that at least one format is enabled
        def custom_validator(validated):
            if not any(validated.values()):
                raise ValueError(
                    'The timestamp source requires at least one timestamp '
                    'format enabled'
                )

        config.add_validator(custom_validator)


Logging Considerations
======================

Both :term:`sources <Source>` and :term:`sinks <Sink>` run in subprocesses, so
logging and printing directly to ``stdout`` or ``stderr`` will mangle the
output. In order to log and print from any context without issues Flowbber
provides the functions:

#. :func:`flowbber.logging.get_logger` that allows to get a multiprocess safe
   logger.
#. :func:`flowbber.logging.print` that allows to safely print to ``stdout`` or
   ``stderr`` in a multiprocess context.

.. autofunction:: flowbber.logging.get_logger
   :noindex:

.. autofunction:: flowbber.logging.print
   :noindex:

Nevertheless, it is important to note that in Flowbber, Python's traditional
:py:func:`logging.getLogger` loggers will also work correctly, for example,
inside a third party library used in your sources or sinks. So no change needs
to be done if Flowbber's ``get_logger`` function isn't used for logging, it is
just the recommended one.

**Usage:**

.. code-block:: python3

    from flowbber.logging import get_logger, print


    log = get_logger(__name__)


    def do_foo(say):
        print(say)
        print(say, fd='stderr')
        log.info(say)


Pipeline API Usage
==================

It is possible to build a Python package that implements a specific pipeline
based on Flowbber.

For example, consider a daemon that reads values from connected Arduino based
sensors inside a RaspberryPI and submits it to a server in the cloud, either
using a web service or a database management system.

As another example consider a monitoring daemon that grabs the CPU usage
information from the system and submits it to a InfluxDB_ and / or MongoDB_
database.

.. _InfluxDB: https://www.influxdata.com/time-series-platform/influxdb/
.. _MongoDB: https://www.mongodb.com/

Let's code a basic version of our hypothetical daemon ``cpud``. Let's assume
that its configuration file is located at ``/etc/cpud.toml`` and look like
this:

.. code-block:: toml

    [cpud]
    verbosity = 3

    # Take a sample each 10 seconds
    frequency = 10

    [influxdb]
    uri = "influxdb://localhost:8086/"
    database = "cpud"

    [mongodb]
    uri = "mongodb://localhost:27017/"
    database = "cpud"
    collection = "cpuddata"

A basic and naive implementation of such daemon could looks like this:

.. code-block:: python3

    from toml import loads

    from flowbber.pipeline import Pipeline
    from flowbber.scheduler import Scheduler
    from flowbber.logging import setup_logging


    def build_definition(config):
        """
        Build a pipeline definition based on given configuration.
        """
        definition = {
            'sources': [
                {'type': 'timestamp', 'id': 'timekeys', 'config': {
                    'epoch': True,  # Key for MongoDB
                    'iso8601': True,  # Key for InfluxDB
                }},
                {'type': 'cpu', 'id': 'cpu'},
            ],
            'sinks': [],
            'aggregators': [],
        }

        if config['influxdb']:
            definition['sinks'].append({
                'type': 'influxdb',
                'id': 'influxdb',
                'config': {
                    'uri': config['influxdb']['uri'],
                    'database': config['influxdb']['database'],
                    'key': 'timekeys.iso8601',
                }
            })

        if config['mongodb']:
            definition['sinks'].append({
                'type': 'mongodb',
                'id': 'mongodb',
                'config': {
                    'uri': config['mongodb']['uri'],
                    'database': config['mongodb']['database'],
                    'collection': config['mongodb']['collection'],
                    'key': 'timekeys.epoch',
                }
            })

        if not definition['sinks']:
            raise RuntimeError('No sinks configured')

        return definition


    def main():

        # Read configuration
        with open('/etc/cpud.toml') as fd:
            config = loads(fd.read())

        # Setup multiprocess logging
        setup_logging(config['cpud']['verbosity'])

        # Build pipeline definition
        definition = build_definition(config)

        # Build pipeline
        pipeline = Pipeline(
            definition,
            'cpud',
            app='cpud',
            save_journal=False,
        )

        # Build and run scheduler
        scheduler = Scheduler(
            pipeline,
            config['cpud']['frequency'],
            stop_on_failure=True
        )

        scheduler.run()


The most relevant parts of this example is that:

#. We programmatically build the :term:`Pipeline Definition` from
   ``cpud``'s own configuration file.

   Note that the package itself could package the required
   :term:`components <Component>` (Sources, Aggregators or Sinks) altogether.

#. We create an instance of :class:`flowbber.pipeline.Pipeline` with the
   definition.

   For one time execution applications we can use
   :meth:`flowbber.pipeline.Pipeline.run` method.

   .. autoclass:: flowbber.pipeline.Pipeline
      :members:
      :noindex:

#. We create an instance of :class:`flowbber.scheduler.Scheduler` that will
   control the continuous execution of the pipeline.

   .. autoclass:: flowbber.scheduler.Scheduler
      :members:
      :noindex:

#. We first thing we do is call :func:`flowbber.logging.setup_logging` with the
   configured verbosity level to setup Flowbber's multiprocess safe logging and
   printing.

   If this function isn't called as soon as possible or not called at all then
   logging performed from sources and sinks that run in their own subprocess
   will mangle the logging output.

   .. autofunction:: flowbber.logging.setup_logging
      :noindex:
