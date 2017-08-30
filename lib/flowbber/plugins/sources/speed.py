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

Speed
=====

This source collects the network bandwidth the system curretly has
using `Speedtest.net <http://speedtest.net/>`_ servers.

Three metrics are collected:

- ``ping``: Latency, in milliseconds.
- ``download``: Download speed, in bits per second.
- ``upload``: Upload speed, in bits per second.

**Data collected:**

.. code-block:: json

    {
        "ping": 9.306252002716064,
        "download": 42762976.92544772,
        "upload": 19425388.307319913
    }

**Dependencies:**

.. code-block:: sh

    pip3 install flowbber[speed]

**Usage:**

.. code-block:: json

    {
        "sources": [
            {
                "type": "speed",
                "id": "...",
                "config": {
                    "host": null,
                    "runs": 2
                }
            }
        ]
    }

host
----

Use a specific server.

- **Default**: ``None``
- **Optional**: ``True``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'string',
         'empty': False,
         'nullable': True,
     }

- **Secret**: ``False``

runs
----

Number of runs to perform.

- **Default**: ``2``
- **Optional**: ``True``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'list',
         'schema': {
             'type': 'integer',
             'min': 1,
         },
     }

- **Secret**: ``False``

"""  # noqa

from flowbber.components import Source
from flowbber.logging import get_logger


log = get_logger(__name__)


class SpeedSource(Source):

    def declare_config(self, config):
        config.add_option(
            'host',
            default=None,
            optional=True,
            schema={
                'type': 'string',
                'empty': False,
                'nullable': True,
            },
        )

        config.add_option(
            'runs',
            default=2,
            optional=True,
            schema={
                'type': 'integer',
                'min': 1,
            },
        )

    def collect(self):
        from pyspeedtest import SpeedTest

        test = SpeedTest(
            host=self.config.host.value,
            runs=self.config.runs.value,
        )

        data = {
            'ping': test.ping(),
            'download': test.download(),
            'upload': test.upload(),
        }

        return data


__all__ = ['SpeedSource']
