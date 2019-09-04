# -*- coding: utf-8 -*-
#
# Copyright (C) 2017-2019 KuraLabs S.R.L
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""

Data Splitter Sink
==================

This sink creates files with certain information from the whole data
collected. The user needs to specify what data he/she wants to extract,
which unique id to use for each file, where the files will be stored and
what format does he/she wants for the file.

.. important::

   This class inherits several inclusion and exclusion configuration options
   for filtering data before using it. See :ref:`filter-sink-options` for more
   information.

**Dependencies:**

.. code-block:: sh

    pip3 install flowbber[data_splitter]

**Usage:**

.. code-block:: toml

    [[sinks]]
    type = "data_splitter"
    id = "..."

        [sinks.config]
        create_parents = true
        output = ".../hardware"
        id_selector = "hardware.suites.pytest.tests.*"
        data_selector = "hardware.suites.pytest.*"
        format = "str"

.. code-block:: json

    {
        "sinks": [
            {
                "type": "data_splitter",
                "id": "...",
                "config": {
                    "create_parents": true,
                    "output": ".../hardware",
                    "id_selector": "hardware.suites.pytest.tests.*",
                    "data_selector": "hardware.suites.pytest.*"
                }
            }
        ]
    }

encoding
--------

Encoding to use to encode the file.

- **Default**: ``utf-8``
- **Optional**: ``True``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'string',
         'empty': False,
     }

- **Secret**: ``False``

output
------

Pattern to a path to where collected data files will be stored.
The path should use the ``{{id}}`` replacement pattern to allow the sink to
determine its final path using the IDs found.

For example::

    path = "/tmp/myfiles/{{id}}/{{id}}.yaml"

- **Default**: ``N/A``
- **Optional**: ``False``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'string',
         'empty': False,
     }

- **Secret**: ``False``

create_parents
--------------

Create output file parent directories if don't exist.

- **Default**: ``False``
- **Optional**: ``True``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'boolean',
     }

- **Secret**: ``False``

id_selector
-----------

Selector is a pattern using fnmatch that matches branches in the data tree.
The branches found will be used as ID for the filenames.

- **Default**: ``N/A``
- **Optional**: ``False``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'list',
         'empty': False,
     }

- **Secret**: ``False``

data_selector
-------------

Selector is a pattern using fnmatch that matches branches in the data tree.
The branches found will be used as the data of the files.

- **Default**: ``N/A``
- **Optional**: ``False``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'list',
         'empty': False,
     }

- **Secret**: ``False``

format
------

File format that will be used to store the data.

- **Default**: ``json``
- **Optional**: ``true``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'string',
         'empty': False,
         'allowed': ['yaml', 'json', 'toml', 'str']
     }

- **Secret**: ``False``
"""  # noqa

from pathlib import Path
from copy import deepcopy
from fnmatch import fnmatch
from collections import deque, OrderedDict

from flowbber.components import FilterSink
from flowbber.logging import get_logger


log = get_logger(__name__)


class DataSplitterSink(FilterSink):
    def declare_config(self, config):
        super().declare_config(config)

        config.add_option(
            'encoding',
            default='utf-8',
            optional=True,
            schema={
                'type': 'string',
                'empty': False,
            },
        )
        config.add_option(
            'output',
            optional=False,
            schema={
                'type': 'string',
                'empty': False
            },
        )
        config.add_option(
            'create_parents',
            default=True,
            optional=True,
            schema={
                'type': 'boolean',
            },
        )
        config.add_option(
            'id_selector',
            optional=False,
            schema={
                'type': 'string',
                'empty': False
            },
        )
        config.add_option(
            'data_selector',
            optional=False,
            schema={
                'type': 'string',
                'empty': False
            },
        )
        config.add_option(
            'format',
            optional=True,
            default='json',
            schema={
                'type': 'string',
                'empty': False,
                'allowed': ['yaml', 'json', 'toml', 'str']
            },
        )

    def distribute(self, data):

        # Filter data wanted by the user
        super().distribute(data)

        # This function returns the data that will be used on the files
        def data_finder(sub_data, patterns, id_selector):
            pattern = patterns.popleft()
            if isinstance(sub_data, list):
                sub_data = OrderedDict(enumerate(sub_data))

            if pattern == '*':
                # Substitute the wildcard with the corresponding id
                pattern = id_selector

            try:
                # End of the data selector return the data subtree
                if not patterns:
                    return sub_data[pattern]
                else:
                    return data_finder(
                        sub_data[pattern], patterns, id_selector
                    )
            except KeyError as e:
                raise KeyError(
                    'During the data search, the key "{}" is not present in'
                    ' the data. The data is: {}'.format(key, sub_data)
                ) from e

        # This function returns the names that will be used on the files
        def ids_finder(key, sub_data, patterns, ids):
            pattern = patterns.popleft()

            if not fnmatch(str(key), pattern):
                return

            # The user wants to use dict keys as the filenames
            if not patterns and pattern == '*':
                ids.append(key)
                return

            # Keep searching...
            scalar = True
            if isinstance(sub_data, dict):
                scalar = False
                data_iter = sub_data.items()
            elif isinstance(sub_data, list):
                scalar = False
                data_iter = enumerate(sub_data)

            # The user wants to use a dict value as the filename
            if scalar:
                ids.append(str(sub_data))
            else:
                for key, sub_dict in data_iter:
                    ids_finder(
                        key, sub_dict, deepcopy(patterns), ids
                    )

        ids = []
        for key, value in data.items():
            ids_finder(
                key, value, deque(self.config.id_selector.value.split('.')),
                ids
            )

        log.info(
            'The IDs chosen are: {}'.format(
                ','.join([str(id) for id in ids])
            )
        )

        # Builds a dictionary that maps the ids with the
        # data that will be used for each one. The dictionary has the form:
        #
        # {
        #   id_1: {...},
        #   id_2: {...},
        #   ....
        # }
        ids_data_map = {
            identifier: data_finder(
                deepcopy(data),
                deque(self.config.data_selector.value.split('.')),
                identifier
            ) for identifier in ids
        }

        file_format = self.config.format.value
        for identifier, data in ids_data_map.items():

            output_file = Path(self.config.output.value.format(id=identifier))

            # Create parent directories
            if self.config.create_parents.value:
                output_file.parent.mkdir(parents=True, exist_ok=True)

            if not output_file.parent.is_dir():
                raise FileNotFoundError(
                    'No such directory {}'.format(output_file.parent)
                )

            if file_format == 'yaml':
                import yaml
                # What this mysterious code is doing to the yaml is adding a
                # special serialization to the classes OrderedDict and tuple.
                # This allows a way better visualization of the files, avoiding
                # things like: !!python/object/apply:collections.OrderedDict in
                # the middle of the output file. Please check the official docs
                # for more info: https://pyyaml.org/wiki/PyYAMLDocumentation
                # under constructors, representers, resolvers section.
                yaml.add_representer(
                    OrderedDict, lambda dumper,
                    data: dumper.represent_mapping(
                        'tag:yaml.org,2002:map', data.items()
                    )
                )
                yaml.add_representer(
                    tuple, lambda dumper,
                    data: dumper.represent_sequence(
                        'tag:yaml.org,2002:seq', data
                    )
                )
                content = yaml.dump(data)
            elif file_format == 'json':
                from ujson import dumps
                content = dumps(data)
            elif file_format == 'toml':
                from toml import dumps
                content = dumps(data)
            else:
                content = str(data)
            output_file.write_text(
                content, encoding=self.config.encoding.value
            )


__all__ = ['DataSplitterSink']
