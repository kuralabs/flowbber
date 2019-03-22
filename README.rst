======================================
Flowbber - The Data Pipeline Framework
======================================

Flowbber is a generic tool and framework that allows to execute custom
pipelines for data gathering, publishing and analysis.

.. image:: https://build.kuralabs.io/buildStatus/icon?job=GitHub/flowbber/master
   :target: https://build.kuralabs.io/job/GitHub/job/flowbber/job/master/
   :alt: Build Status


Documentation
=============

    https://docs.kuralabs.io/flowbber/


Install
=======

.. code-block:: sh

    pip3 install flowbber


Changelog
=========

1.7.0 (2019-03-22)
------------------

New
~~~

- New ``--dry-run`` flag allows to parse, load, validate and build a pipeline
  without executing it.

Changes
~~~~~~~

- Improved logging when trying to instance a component to help debugging a
  pipeline that went wrong.
- Improved logging to show a log in higher level when things go bad.

Fixes
~~~~~

- Fix for missing plugin entries in documentation.
- Fix for documentation issue #27.


1.6.0 (2019-03-12)
------------------

New
~~~

- New LCOV merger aggregator allows to sum multiple LCOV sources.

Fixes
~~~~~

- Fix a bug that ignored ``rc_overrides`` when using a file input in LCOV
  source.


1.5.0 (2019-02-22)
------------------

Changes
~~~~~~~

- lcov source no longer accepts ``directory`` as configuration.
  New option ``source`` superseded it, and allows to specify a directory to
  generate a tracefile or load one already generated.


1.4.0 (2019-01-28)
------------------

New
~~~

- Refactored Valgrind source to support loading data from Helgrind and DRD
  tools.
- New "Expander" aggregator that allows to move subdata to top level. This is
  useful to load data using JSONSource or similar sources and place it in the
  top level as if it were data from other anonymous sources. Or to replay
  a pipeline using previously collected data.


1.3.2 (2018-11-20)
------------------

New
~~~

- Add support for path in InfluxDB sink.

Fixes
~~~~~

- Fixed flake8 issues shown in new version.


1.3.1 (2018-09-19)
------------------

Fixes
~~~~~

- Source for Valgrind's memcheck will now always output the ``stack`` attribute
  as a list.


1.3.0 (2018-08-23)
------------------

New
~~~

- New Config source that allows to add arbitrary data directly from the
  pipeline definition.
- All plugins now show the example usage in both JSON and TOML.
- Improved documentation for the memcheck source.

Changes
~~~~~~~

- The Internet speed source plugin is unavailable as the upstream package
  providing the measurement is currently broken:
  https://github.com/fopina/pyspeedtest/issues/15

Fixes
~~~~~

- Fix in pytest source that caused a test case with both failure and error
  to be overridden by the other:
  https://github.com/pytest-dev/pytest/issues/2228
- Minor fix in memcheck source plugin that caused output that violates the
  expected schema.


1.2.1 (2017-11-26)
------------------

Fixes
~~~~~

- The InfluxDB sink is now compatible with influxdb client version 5.0.0.


1.2.0 (2017-11-13)
------------------

New
~~~

- New timezone option for the timestamp source.
- New source for Valgrind's Memcheck.
- Add lcov source and lcov html sink.
- New JSON source for fetch and parse local (file system) or remote
  (http, https) JSON files.
- The CoberturaSource now returns the list of ignored files.
- TemplateSink now support passing filters.
- All sinks can now filter the input data.
- New FilterAggregator allows to filter the data structure before sending it to
  the sinks.
- When using the TemplateSink, extra data can now be passed from the pipeline
  definition to the template by using the new 'payload' configuration option.
  Fixes #5.
- Each entry from the collected data can now be put into its own collection
  when using the MongoDBSink. Fixes #2.
- Added a source that counts lines of code in a directory.
- Added a new Git source that provides revision, tag and author information of
  a git repository.
- New GitHub source that allows to collect statistics of closed / open pull
  requests and issues.
- New Google Test source.
- Added a "pretty" option to the ArchiveSink to make JSON output pretty. Also,
  JSON file is now saved in UTF-8.
- Added new source plugin for pytest's JUnit-like XML test results.
- CoberturaSource now supports filenames include and exclude patterns.

Changes
~~~~~~~

- UserSource no longer returns the login key and instead returns a user key.
- Templates used in the TemplateSink can now load sibling templates.
  Previous way to specify python:// templates changed.
- MongoDBSink now uses None as default for the ``key`` configuration option.
  Related to #4.
- InfluxDBSink now uses None as default for the ``key`` configuration option.
  Related to #4.

Fixes
~~~~~

- Local flowconf can now be reloaded in the same process.
- Fix a deadlock condition when a non-optional component failed with still
  running siblings components.
- Fixes #6 : InfluxDBSink doesn't support None values.
- Journal is now saved in UTF-8.
- Fixed high CPU usage by the logging manager subprocess.
- ``flowbber.logging.print`` will now convert to string any input provided.
- Fix minor typo in EnvSource include / exclude logic.
- The pipeline executor will now join the process of a component (max 100ms)
  after fetching its response in order to try to get its exit code.


1.1.0 (2017-09-07)
------------------

New
~~~

- Added "optional" and "timeout" features to pipeline components.

Changes
~~~~~~~

- Git helpers now live into its own utilities module ``flowbber.utils.git``.

Fixes
~~~~~

- Fixed bug where pipeline execution counter didn't increment.


1.0.0 (2017-08-30)
------------------

New
~~~

- Initial version.


License
=======

::

   Copyright (C) 2017-2018 KuraLabs S.R.L

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing,
   software distributed under the License is distributed on an
   "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
   KIND, either express or implied.  See the License for the
   specific language governing permissions and limitations
   under the License.
