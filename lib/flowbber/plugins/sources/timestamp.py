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

It is recommended to include at least one timestamp source on every pipeline in
order to have a unique and consistent timestamp for the whole pipeline to use.

**Data collected:**

.. code-block:: json

    {
        "timezone": null,
        "epoch": 1502852229,
        "epochf": 1502852229.427491,
        "iso8601": "2017-08-15T20:57:09",
        "strftime": "2017-08-15 20:57:09"
    }

.. code-block:: json

    {
        "timezone": 0,
        "epoch": 1507841667,
        "epochf": 1507841667.9304831028,
        "iso8601": "2017-10-12T20:54:27+00:00",
        "strftime": "2017-10-12 20:54:27"
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
                    "timezone": null,
                    "epoch": true,
                    "epochf": true,
                    "iso8601": true,
                    "strftime": "%Y-%m-%d %H:%M:%S"
                }
            }
        ]
    }

timezone
--------

Specify the timezone for which the timestamp should be calculated. If ``None``
is provided (the default), the timestamp will be calculated using the local
timezone (current time). Use ``0`` for a UTC timestamp, and a +/-12 integer for
any other timezone.

Note that this doesn't affect the ``epoch`` or ``epochf`` timestamps, as those
values are always in POSIX time which is the number of seconds since the Epoch
(1970-01-01 UTC) not counting leap seconds.

- **Default**: ``None``
- **Optional**: ``True``
- **Schema**:

  .. code-block:: python3

     {
        'type': 'integer',
        'nullable': True,
        'max': 12,
        'min': -12,
     }

- **Secret**: ``False``

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
            'timezone',
            default=None,
            optional=True,
            schema={
                'type': 'integer',
                'nullable': True,
                'max': 12,
                'min': -12,
            },
        )

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
            timeformatkeys = ['epoch', 'epochf', 'iso8601', 'strftime']
            if not any(validated[key] for key in timeformatkeys):
                raise ValueError(
                    'The timestamp source requires at least one timestamp '
                    'format enabled'
                )

        config.add_validator(custom_validator)

    def collect(self):
        from datetime import datetime, timezone, timedelta

        # Get timezone
        tz = None
        tzdelta = self.config.timezone.value

        if tzdelta is not None:
            tz = timezone(timedelta(hours=tzdelta))

        now = datetime.now(tz=tz)

        entry = {
            'timezone': tzdelta
        }

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
