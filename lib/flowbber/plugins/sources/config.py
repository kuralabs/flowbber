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

Config
======

This sources let the user indicate static data to describe current pipeline.

**Data collected:**

*Anything the user entered on the configuration*

**Dependencies:**

.. code-block:: sh

    pip3 install flowbber[config]

**Usage:**

.. code-block:: toml

    [[sources]]
    type = "config"
    id = "..."

        [sources.config.data]
        anydata = "...."

.. code-block:: json

    {
        "sources": [
            {
                "type": "config",
                "id": "...",
                "config": {
                    "data": {
                        "anydata": "...."
                    }
                }
            }
        ]
    }


data
----

Free off schema data.

- **Default**: ``False``
- **Optional**: ``False``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'dict'
     }

- **Secret**: ``False``

"""  # noqa

from copy import deepcopy

from flowbber.components import Source


class ConfigSource(Source):

    def declare_config(self, config):
        config.add_option(
            'data',
            schema={
                'type': 'dict',
                'empty': False,
            },
        )

    def collect(self):
        return deepcopy(self.config.data.value)


__all__ = ['ConfigSource']
