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
