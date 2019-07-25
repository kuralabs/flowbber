========
Flowbber
========

.. container:: float-right

   .. image:: _static/images/flowbber.svg

Flowbber provides a tool and framework that allows to create and execute
custom pipelines for data collection, analysis and publishing.

.. code-block:: console

   $ cat pipeline.toml
   [[sources]]
   type = "timestamp"
   id = "timestamp1"

   [[sources]]
   type = "cpu"
   id = "cpu1"

   [[sinks]]
   type = "print"
   id = "print1"

   $ flowbber pipeline.toml
   OrderedDict([
       ('timestamp1', {'epoch': 1519166006, 'timezone': None}),
       ('cpu1', {'num_cpus': 4, 'per_cpu': [1.0, 3.0, 5.0, 2.0], 'system_load': 2.75}),
   ])

.. toctree::
   :maxdepth: 2

   quickstart

.. toctree::
   :maxdepth: 3

   implementation
   dynamic

.. toctree::
   :maxdepth: 2

   visualization


Plugins
=======

Flowbber has batteries included with a set of commonly used plugins:

.. toctree::
   :maxdepth: 2

   sources
   aggregators
   sinks


Development
===========

.. toctree::
   :maxdepth: 2

   developer
   API Reference <flowbber/flowbber>
   Source Code <https://github.com/kuralabs/flowbber>


License
=======

.. code-block:: text

   Copyright (C) 2017-2019 KuraLabs S.R.L

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
