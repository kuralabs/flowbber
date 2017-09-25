# -*- coding: utf-8 -*-
#
# Copyright (C) 2017 KuraLabs S.R.L
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

Filter
======

Filter the collected data structure using the provided include and exclude
patterns.

For example, consider a collected data that looks as following:

.. code-block:: python3

    OrderedDict([
        ('my_source', {
            'my_value1': 1000,
            'my_value2': 2000,
            'my_value3': 3000,
            'other_value': 'hello'
        }),
        ('coverage', {
            'files': {
                '__init__.py': {
                    'line_rate': 1.0,
                    'total_misses': 0,
                    'total_statements': 4,
                },
                '__main__.py': {
                    'line_rate': 0.5,
                    'total_misses': 5,
                    'total_statements': 10,
                },
            },
            'total': {
                'line_rate': 0.37275985663082434,
                'total_misses': 350,
                'total_statements': 558,
            },
        }),
    ])

And you want to remove all the ``my_value*`` keys from ``my_source`` and all
``files`` entries in ``coverage``. If using the configuration:

.. code-block:: toml

    [[aggregators]]
    type = "filter"
    id = "filter"

        [aggregators.config]
        include = ["*"]
        exclude = ["my_source.my_value*", "coverage.files"]

The data will be filtered to:

.. code-block:: python3

    OrderedDict([
        ('my_source', {
            'other_value': 'hello'
        }),
        ('coverage', {
            'total': {
                'line_rate': 0.37275985663082434,
                'total_misses': 350,
                'total_statements': 558,
            },
        }),
    ])

**Dependencies:**

.. code-block:: sh

    pip3 install flowbber[filter]

**Usage:**

.. code-block:: json

    {
        "aggregators": [
            {
                "type": "filter",
                "id": "filter",
                "config": {
                    "include": ["*"],
                    "exclude": []
                }
            }
        ]
    }


include
-------

List of patterns of key paths to include.

Matching is performed using Python's fnmatch_.

.. _fnmatch: https://docs.python.org/3/library/fnmatch.html#fnmatch.fnmatch

- **Default**: ``['*']``
- **Optional**: ``True``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'list',
         'schema': {
             'type': 'string',
             'empty': False,
         },
     }

- **Secret**: ``False``

exclude
-------

List of patterns of key paths to exclude.

Matching is performed using Python's fnmatch_.

.. _fnmatch: https://docs.python.org/3/library/fnmatch.html#fnmatch.fnmatch

- **Default**: ``[]``
- **Optional**: ``True``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'list',
         'schema': {
             'type': 'string',
             'empty': False,
         },
     }

- **Secret**: ``False``

"""  # noqa

from flowbber.logging import get_logger
from flowbber.components import Aggregator
from flowbber.utils.filter import filter_dict


log = get_logger(__name__)


class FilterAggregator(Aggregator):

    def declare_config(self, config):
        config.add_option(
            'include',
            default=['*'],
            optional=True,
            schema={
                'type': 'list',
                'schema': {
                    'type': 'string',
                },
            },
        )

        config.add_option(
            'exclude',
            default=[],
            optional=True,
            schema={
                'type': 'list',
                'schema': {
                    'type': 'string',
                },
            },
        )

    def accumulate(self, data):
        filtered = filter_dict(
            data,
            self.config.include.value,
            self.config.exclude.value,
        )
        data.clear()
        data.update(filtered)


__all__ = ['FilterAggregator']
