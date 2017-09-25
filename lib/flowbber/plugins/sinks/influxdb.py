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

InfluxDB
========

This sink writes all collected data to a InfluxDB_ time series database.

.. _InfluxDB: https://www.influxdata.com/time-series-platform/influxdb/

In order to be able to track in time the complex data collected by the sources
this sink requires to "flatten" the data first. The process will transform an
arbitrarily deep dictionary tree into a fixed depth dictionary that maps the
keys of the sources with the measurements they performed.

To accomplish this, the flattening process will:

- Join all dictionaries keys (using the ``keysjoiner`` character) until a leaf
  value that has a datatype supported by InfluxDB (string, float, integer,
  boolean or None) is found.

- Lists are converted to a dictionary that maps the index of the element
  with the element previous to the flattening.

So, for example, consider the data collected by the ``Cobertura`` source:

.. code-block:: python3

    {
        'coverage': {
            'files': {
                '__init__.py': {
                    'line_rate': 1.0,
                    'total_misses': 0,
                    'total_statements': 10,
                },
                '__main__.py': {
                    'line_rate': 0.5,
                    'total_misses': 5,
                    'total_statements': 10,
                },
                # ...
            },
            'total': {
                'line_rate': 0.75,
                'total_misses': 5,
                'total_statements': 20,
            }
        }
    }

The above structure will be transformed into:

.. code-block:: python3

    {
        'coverage': {
            'files.__init__:py.line_rate': 1.0,
            'files.__init__:py.total_misses': 0,
            'files.__init__:py.total_statements': 10,
            'files.__main__:py.line_rate': 0.5,
            'files.__main__:py.total_misses': 5,
            'files.__main__:py.total_statements': 10,
            # ...
            'total.line_rate': 0.75,
            'total.total_misses': 5,
            'total.total_statements': 20,
        }
    }

.. important::

    Please note the ``.`` in the file name was changed to ``:`` before joining
    the keys. This replacement and joining is controlled by the
    ``keysjoinerreplace`` and ``keysjoiner`` options.

    Also note that the leaf keys must map to a value that can be used as field
    value in InfluxDB (string, float, integer, boolean or None), if not, the
    flattening will fail.

Or in case of lists:

.. code-block:: python3

    {
        'key1': ['a', 'b', 'c'],
        'key2': [
            {'a': 1},
            {'b': 2},
            {'c': 3},
        ]
    }

The flattening results in:

.. code-block:: python3

    {
        'key.0' : 'a',
        'key.1' : 'b',
        'key.2' : 'c',
        'key.0.a' : 1,
        'key.1.b' : 2,
        'key.2.c' : 3,
    }

You may run this sink with ``DEBUG`` verbosity (``-vvv``) to analyze all
transformations performed.

**Dependencies:**

.. code-block:: sh

    pip3 install flowbber[influxdb]

**Usage:**

.. code-block:: json

    {
        "sinks": [
            {
                "type": "influxdb",
                "id": "...",
                "config": {
                    "uri": "influxdb://localhost:8086/",
                    "database": "flowbber",
                    "key": "timestamp.iso8601"
                }
            }
        ]
    }

uri
---

URI to connect to InfluxDB.

If this is set, options ``host``, ``port``, ``username``, ``password`` and
``ssl`` will be ignored.

URI is in the form:

.. code-block:: text

    influxdb://username:password@localhost:8086/

Supported schemes are ``influxdb``, ``https+influxdb`` and ``udp+influxdb``.

Check function from_DSN_ for more information.

.. _from_DSN: http://influxdb-python.readthedocs.io/en/latest/api-documentation.html#influxdb.InfluxDBClient.from_DSN

- **Default**: ``None``
- **Optional**: ``True``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'string',
         'empty': False,
         'nullable': True,
     }

- **Secret**: ``True``

host
----

Hostname or IP to connect to InfluxDB.

- **Default**: ``localhost``
- **Optional**: ``True``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'string',
         'empty': False,
     }

- **Secret**: ``False``

port
----

Port to connect to InfluxDB.

- **Default**: ``8086``
- **Optional**: ``True``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'integer',
         'min': 0,
         'max': 65535,
     }

- **Secret**: ``False``

username
--------

User to connect to InfluxDB.

- **Default**: ``root``
- **Optional**: ``True``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'string',
         'empty': False,
     }

- **Secret**: ``False``

password
--------

Password of the user.

- **Default**: ``root``
- **Optional**: ``True``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'string',
     }

- **Secret**: ``True``

ssl
---

Use https instead of http to connect to InfluxDB.

- **Default**: ``False``
- **Optional**: ``True``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'boolean',
     }

- **Secret**: ``False``

verify_ssl
----------

Verify SSL certificates for HTTPS requests.

- **Default**: ``False``
- **Optional**: ``True``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'boolean',
     }

- **Secret**: ``False``

database
--------

Database name to connect to.

- **Default**: ``N/A``
- **Optional**: ``False``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'string',
         'empty': False,
     }

- **Secret**: ``False``

key
---

Path to a value in the collected data that will be used as key timestamp when
submitting the flattened data to the database.

Specify the path to the value by joining keys path with a ``.`` (dot).

For example given the following structure:

.. code-block:: python3

    {
        'my_key': {
            'a_sub_key': {
                'yet_another': '2017-08-19T01:26:35.683529'
            }
        }
    }

The corresponding path to use the value ``2017-08-19T01:26:35.683529`` as
timestamp is ``my_key.a_sub_key.yet_another``.

This option is nullable, and if null is provided (the default), the timestamp
will be determined when submitting the data by calling Python's
``datetime.now().isoformat()``.

In order to have a single timestamp for your pipeline you can include the
:ref:`Timestamp <sources-timestamp>` source and use a configuration similar to
the following:

.. code-block:: toml

    [[sources]]
    type = "timestamp"
    id = "timestamp"

        [sources.config]
        iso8601 = true

    [[sinks]]
    type = "influxdb"
    id = "..."

        [sinks.config]
        uri = "..."
        database = "..."
        key = "timestamp.iso8601"

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

keysjoiner
----------

Character used to join the keys when flattening the collected data (see data
flattening process above).

- **Default**: ``.``
- **Optional**: ``True``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'string',
     }

- **Secret**: ``False``

keysjoinerreplace
-----------------

Character used to replace occurrences of the ``keysjoiner`` character in the
keys of the collected data previous to flatten it.

This option is nullable, and if null is provided, no character replacement to
the keys will be done.

- **Default**: ``:``
- **Optional**: ``True``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'string',
         'nullable': True,
     }

- **Secret**: ``False``

"""  # noqa

from datetime import datetime

from pprintpp import pformat

from flowbber.logging import get_logger
from flowbber.components import FilterSink


log = get_logger(__name__)


def transform_to_flat(data, keysjoiner, keysjoinerreplace):
    """
    Flatten the collected data to prepare it for submission to the database.

    The general process is as follow:

    - Join all dictionaries keys in an arbitrarily deep dictionary tree until
      a leaf value (that has a datatype supported by InfluxDB) is found.

    - Lists are converted to a dictionary that maps the index of the element
      with the element previous to the flattening.
    """
    influxdb_supported = (str, int, float, bool, type(None))

    def joinkey(path, key):
        parts = [*path, key]

        if keysjoinerreplace is not None:
            parts = [
                part.replace(keysjoiner, keysjoinerreplace)
                for part in parts
            ]

        return keysjoiner.join(parts)

    def flat(dictionary, path):
        assert isinstance(dictionary, dict)

        for key, value in dictionary.items():
            if isinstance(value, influxdb_supported):
                yield joinkey(path, key), value
                continue

            if isinstance(value, dict):
                yield from flat(value, path + [key])
                continue

            if isinstance(value, list):
                value_as_dict = {
                    str(index): subvalue
                    for index, subvalue in enumerate(value)
                }
                yield from flat(value_as_dict, path)
                continue

            raise ValueError('Unable to flat value ({}): {}'.format(
                type(value), value
            ))

    return {
        key: {
            subkey: subvalue
            for subkey, subvalue in flat(value, [])
        }
        for key, value in data.items()
    }


def transform_to_points(timestamp, flat):
    """
    Transform a dictionary of flattened collected data into a list of points.

    A Point is a concrete data structure that InfluxDB understand::

        {
            "measurement": "cpu_load_short",
            "tags": {
                "host": "server01",
                "region": "us-west"
            },
            "time": "2009-11-10T23:00:00Z",
            "fields": {
                "value": 0.64
            }
        }

    Field value must be string, float, integer, or boolean.
    """
    points = [
        {
            'measurement': source,
            'tags': {},
            'time': timestamp,
            'fields': {
                key: value
                for key, value in collected.items()
            }
        }
        for source, collected in flat.items()
    ]

    return points


class InfluxDBSink(FilterSink):
    def declare_config(self, config):
        super().declare_config(config)

        # Connection options
        config.add_option(
            'uri',
            default=None,
            optional=True,
            schema={
                'type': 'string',
                'empty': False,
                'nullable': True,
            },
            secret=True,
        )

        config.add_option(
            'host',
            default='localhost',
            optional=True,
            schema={
                'type': 'string',
                'empty': False,
            },
        )

        config.add_option(
            'port',
            default=8086,
            optional=True,
            schema={
                'type': 'integer',
                'min': 0,
                'max': 65535,
            },
        )

        config.add_option(
            'username',
            default='root',
            optional=True,
            schema={
                'type': 'string',
                'empty': False,
            },
        )

        config.add_option(
            'password',
            default='root',
            optional=True,
            schema={
                'type': 'string',
            },
            secret=True,
        )

        config.add_option(
            'ssl',
            default=False,
            optional=True,
            schema={
                'type': 'boolean',
            },
        )

        config.add_option(
            'verify_ssl',
            default=False,
            optional=True,
            schema={
                'type': 'boolean',
            },
        )

        # Data options
        config.add_option(
            'database',
            schema={
                'type': 'string',
                'empty': False,
            },
        )

        config.add_option(
            'key',
            default=None,
            optional=True,
            schema={
                'type': 'string',
                'empty': False,
                'nullable': True,
            },
        )

        config.add_option(
            'keysjoiner',
            default='.',
            optional=True,
            schema={
                'type': 'string',
            },
        )

        config.add_option(
            'keysjoinerreplace',
            default=':',
            optional=True,
            schema={
                'type': 'string',
                'nullable': True,
            },
        )

        # Check if uri is defined and if so then delete other keys
        def custom_validator(validated):
            if validated['uri'] is not None:
                del validated['host']
                del validated['port']
                del validated['username']
                del validated['password']
                del validated['ssl']
            else:
                del validated['uri']

        config.add_validator(custom_validator)

    def distribute(self, data):
        from influxdb import InfluxDBClient

        # Allow to filter data
        super().distribute(data)

        # Get key
        if self.config.key.value is None:
            key = datetime.now().isoformat()

        else:
            current = data
            for part in self.config.key.value.split('.'):
                current = current[part]

            key = current

        # Connect to database
        if self.config.uri.value is None:
            client = InfluxDBClient(
                host=self.config.host.value,
                port=self.config.port.value,
                username=self.config.username.value,
                password=self.config.password.value,
                database=self.config.database.value,
                ssl=self.config.ssl.value,
                verify_ssl=self.config.verify_ssl.value,
            )
        else:
            client = InfluxDBClient.from_DSN(
                self.config.uri.value,
                database=self.config.database.value,
                verify_ssl=self.config.verify_ssl.value,
            )

        # Flat data
        log.info('Flattening data for InfluxDB')
        flat = transform_to_flat(
            data,
            self.config.keysjoiner.value,
            self.config.keysjoinerreplace.value,
        )
        del data  # Release a bit of ram here
        log.debug('Flat data:\n{}'.format(pformat(flat)))

        # Insert points
        log.info('Creating points using timestamp {}'.format(key))
        points = transform_to_points(key, flat)
        del flat  # Release a bit of ram here
        log.debug('Points data:\n{}'.format(pformat(points)))

        log.info('Inserting points to InfluxDB: {}'.format([
            point['measurement'] for point in points
        ]))
        client.write_points(points)


__all__ = ['InfluxDBSink']
