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

Timestamp
=========

This source allows to collect timestamps in several formats.

It is recommended to include this block on every pipeline, in particular
because by default some database sinks may use the data provided by this source
as the primary key (although this can be changed on those sinks).

**Data collected:**

.. code-block:: json

    {
        "epoch": 1502852229,
        "epochf": 1502852229.427491,
        "iso8601": "2017-08-15T20:57:09",
        "strftime": "2017-08-15 20:57:09"
    }

**Dependencies:**

.. code-block:: sh

    pip3 install flowbber[timestamp]

**Usage:**

.. code-block:: json

    {
        "sources": [
            {
                "type": "timestamp",
                "id": "...",
                "config": {
                    "epoch": true,
                    "epochf": true,
                    "iso8601": true,
                    "strftime": "%Y-%m-%d %H:%M:%S"
                }
            }
        ]
    }

epoch
-----

Include seconds since the EPOCH, as integer.

- **Default**: ``True``
- **Optional**: ``True``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'boolean',
     }

- **Secret**: ``False``

epochf
------

Include seconds since the EPOCH, as float.

- **Default**: ``False``
- **Optional**: ``True``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'boolean',
     }

- **Secret**: ``False``

iso8601
-------

Include current time as a ISO 8601 string using the ``seconds`` time
specification.

- **Default**: ``False``
- **Optional**: ``True``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'boolean',
     }

- **Secret**: ``False``

strftime
--------

Include a string timestamp using a custom format supported by Python's
strftime_ function.

.. _strftime: https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior

For example: ``"%Y-%m-%d %H:%M:%S"``

- **Default**: ``None``
- **Optional**: ``True``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'string',
         'empty': False,
     }

- **Secret**: ``False``

"""  # noqa

from flowbber.components import Source


class TimestampSource(Source):

    def declare_config(self, config):
        config.add_option(
            'epoch',
            default=True,
            optional=True,
            schema={
                'type': 'boolean',
            },
        )

        config.add_option(
            'epochf',
            default=False,
            optional=True,
            schema={
                'type': 'boolean',
            },
        )

        config.add_option(
            'iso8601',
            default=False,
            optional=True,
            schema={
                'type': 'boolean',
            },
        )

        config.add_option(
            'strftime',
            default=None,
            optional=True,
            schema={
                'type': 'string',
                'empty': False,
            },
        )

        # Check that at least one format is enabled
        def custom_validator(validated):
            if not any(validated.values()):
                raise ValueError(
                    'The timestamp source requires at least one timestamp '
                    'format enabled'
                )

        config.add_validator(custom_validator)

    def collect(self):
        from datetime import datetime

        now = datetime.now()

        entry = {}

        if self.config.epoch.value:
            entry[self.config.epoch.key] = int(now.timestamp())

        if self.config.epochf.value:
            entry[self.config.epochf.key] = now.timestamp()

        if self.config.iso8601.value:
            entry[self.config.iso8601.key] = \
                now.replace(microsecond=0).isoformat()

        if self.config.strftime.value:
            entry[self.config.strftime.key] = \
                now.strftime(self.config.strftime.value)

        # FIXME: Understand and maybe add RFC 3339 timestamp

        return entry


__all__ = ['TimestampSource']
