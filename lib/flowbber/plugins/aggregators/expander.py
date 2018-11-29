# -*- coding: utf-8 -*-
#
# Copyright (C) 2017-2018 KuraLabs S.R.L
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

Expander
========

Takes a value on data and move its contents to the root

For example, consider a collected data that looks as following:

.. code-block:: python3

    OrderedDict([
        ('loaded', OrderedDict([
            ('my_source', {
                'my_value1': 1000,
                'my_value2': 2000,
                'my_value3': 3000,
                'other_value': 'hello'
            }),
        ])),
        ('other_source', {
            'its_value1': 1999,
            'its_value2': 2999,
            'its_value3': 3999,
            'other_value': 'bye'
        }),
    ])


And you want data inside ``loaded`` to be in the top level. If using the
configuration:

.. code-block:: toml

    [[aggregators]]
    type = "expander"
    id = "expander"

        [aggregators.config]
        key = "loaded"

The data will be filtered to:

.. code-block:: python3

    OrderedDict([
        ('my_source', {
            'my_value1': 1000,
            'my_value2': 2000,
            'my_value3': 3000,
            'other_value': 'hello'
        }),
        ('other_source', {
            'its_value1': 1999,
            'its_value2': 2999,
            'its_value3': 3999,
            'other_value': 'bye'
        }),
    ])

**Dependencies:**

.. code-block:: sh

    pip3 install flowbber[expander]

**Usage:**

.. code-block:: toml

    [[aggregators]]
    type = "expander"
    id = "..."

        [aggregators.config]
        key = "..."

.. code-block:: json

    {
        "aggregators": [
            {
                "type": "expander",
                "id": "...",
                "config": {
                    "key": "..."
                }
            }
        ]
    }


key
---

Item to expand to root

- **Optional**: ``False``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'string',
         'empty': False,
     }

- **Secret**: ``False``

"""  # noqa

from flowbber.logging import get_logger
from flowbber.components import Aggregator


log = get_logger(__name__)


class ExpanderAggregator(Aggregator):
    def declare_config(self, config):
        config.add_option(
            'key',
            optional=False,
            schema={
                'type': 'string',
                'empty': False,
            },
        )

    def accumulate(self, data):
        contents = data[self.config.key.value]
        data.pop(self.config.key.value)
        data.update(contents)


__all__ = ['ExpanderAggregator']
