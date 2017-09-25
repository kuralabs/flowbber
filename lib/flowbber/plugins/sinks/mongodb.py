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

MongoDB
=======

This sink writes all collected data to a MongoDB_ NoSQL database.

.. _MongoDB: https://www.mongodb.com/

The collected data is mostly unaltered from its original form, except that
MongoDB document keys cannot contain ``.`` (dot) characters and cannot start
with a ``$`` (dollar) sign.

This sink will transform the keys in the collected data so its safe to submit
it to MongoDB, for this the options ``dotreplace`` and ``dollarreplace`` are
used to perform this transformation.

**Dependencies:**

.. code-block:: sh

    pip3 install flowbber[mongodb]

**Usage:**

.. code-block:: json

    {
        "sinks": [
            {
                "type": "mongodb",
                "id": "...",
                "config": {
                    "uri": "mongodb://localhost:27017/",
                    "database": "flowbber",
                    "collection": "pipeline1data",
                    "key": "timestamp.epoch"
                }
            }
        ]
    }

uri
---

URI to connect to MongoDB.

If this is set, options ``host``, ``port``, ``username`` and ``password`` will
be ignored.

URI is in the form:

.. code-block:: text

    mongodb://username:password@host:port/

Except that for username and password reserved characters like ``:``, ``/``,
``+`` and ``@`` must be percent encoded following RFC 2396:

.. code-block:: python3

    from urllib.parse import quote_plus

    uri = 'mongodb://{}:{}@{}:{}/'.format(
        quote_plus(user),
        quote_plus(password),
        host, port,
    )

``host`` can be a hostname or IP address. Unix domain sockets are also
supported but must be percent encoded:

.. code-block:: python3

    uri = 'mongodb://{}:{}@{}/'.format(
        quote_plus(user),
        quote_plus(password),
        quote_plus(socket_path)
    )

For more information check MongoClient_ API and MongoDocs.

.. _MongoClient: https://api.mongodb.com/python/current/api/pymongo/mongo_client.html#pymongo.mongo_client.MongoClient
.. _MongoDocs: https://docs.mongodb.com/manual/reference/connection-string/

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

Hostname, IP address or Unix domain socket path to connect to MongoDB.

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

Port to connect to MongoDB.

- **Default**: ``27017``
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

User to connect to MongoDB.

- **Default**: ``None``
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

- **Default**: ``None``
- **Optional**: ``True``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'string',
     }

- **Secret**: ``True``

ssl
---

Create the connection to the server using SSL.

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

Database to connect to.

- **Default**: ``N/A``
- **Optional**: ``False``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'string',
         'empty': False,
     }

- **Secret**: ``False``

collection
----------

Collection to write to. This option defines two modes of operation depending if
it is set to ``None`` or any other string value:

1. This option is nullable, if null is provided (the default), the collection
   will be determined for each entry in the collected data bundle using its
   key. For example, given the following pipeline:

   .. code-block:: toml

      [[sources]]
      type = "somesource"
      id = "first_id"

      [[sources]]
      type = "somesource"
      id = "second_id"

      [[sinks]]
      type = "mongodb"
      id = "mongodb"

          [sinks.config]
          uri = "..."
          database = "mydatabase"

   Collects the following data:

   .. code-block:: python3

      {
          'first_id': {
              'abc': 'def',
              'xyz': '123',
          },
          'second_id': {
              '123': 'abc',
              'qwe': 'rty',
          },
      }

   Will be stored in MongoDB as follows:

   1. In collection ``first_id``:

      .. code-block:: python3

         {
             'abc': 'def',
             'xyz': '123',
         }

   2. In collection ``second_id``:

      .. code-block:: python3

         {
             '123': 'abc',
             'qwe': 'rty',
         }

2. Otherwise, the whole data bundle will be stored to the collection specified.

In both cases the ``key`` option will be honored.

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

key
---

Path to a value in the collected data that will be used as object id when
submitting the safe data to the database.

Specify the path to the value by joining keys path with a ``.`` (dot).

For example given the following structure:

.. code-block:: python3

    {
        'my_key': {
            'a_sub_key': {
                'yet_another': 123123123
            }
        }
    }

The corresponding path to use the value ``123123123`` as timestamp is
``my_key.a_sub_key.yet_another``.

This option is nullable, and if null is provided (the default), the object id
will be generated by MongoDB itself.

In order to have a single timestamp for your pipeline you can include the
:ref:`Timestamp <sources-timestamp>` source and use a configuration similar to
the following:

.. code-block:: toml

    [[sources]]
    type = "timestamp"
    id = "timestamp"

        [sources.config]
        epoch = true

    [[sinks]]
    type = "mongodb"
    id = "..."

        [sinks.config]
        uri = "..."
        database = "..."
        collection = "..."
        key = "timestamp.epoch"

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

dotreplace
----------

Character used to replace any occurrence of a ``.`` (dot) character in the keys
of the collected data (see MongoDB data safety above).

- **Default**: ``:``
- **Optional**: ``True``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'string',
     }

- **Secret**: ``False``

dollarreplace
-------------

Character used to replace any occurrence of a ``$`` (dollar) character at the
beginning of any key in the collected data (see MongoDB data safety above).

- **Default**: ``&``
- **Optional**: ``True``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'string',
     }

- **Secret**: ``False``

"""  # noqa

from flowbber.logging import get_logger
from flowbber.components import FilterSink


log = get_logger(__name__)


def mongodb_safe(data, dotreplace, dollarreplace):
    """
    Transform collected data to be MongoDB safe.
    """

    def safe_key(key):
        if key.startswith('$'):
            key = key.replace('$', dollarreplace, 1)

        return key.replace('.', dotreplace)

    def safe_value(value):
        if not isinstance(value, dict):
            return value

        return {
            safe_key(k): safe_value(v)
            for k, v in value.items()
        }

    return safe_value(data)


class MongoDBSink(FilterSink):
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
            default=27017,
            optional=True,
            schema={
                'type': 'integer',
                'min': 0,
                'max': 65535,
            },
        )

        config.add_option(
            'username',
            default=None,
            optional=True,
            schema={
                'type': 'string',
                'empty': False,
            },
        )

        config.add_option(
            'password',
            default=None,
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

        # Data options
        config.add_option(
            'database',
            schema={
                'type': 'string',
                'empty': False,
            },
        )

        config.add_option(
            'collection',
            default=None,
            optional=True,
            schema={
                'type': 'string',
                'empty': False,
                'nullable': True,
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
            'dotreplace',
            default=':',
            optional=True,
            schema={
                'type': 'string',
            },
        )

        config.add_option(
            'dollarreplace',
            default='&',
            optional=True,
            schema={
                'type': 'string',
            },
        )

        # Check if uri is defined and if so then delete other keys
        def custom_validator(validated):
            if validated['uri'] is not None:
                del validated['host']
                del validated['port']
                del validated['username']
                del validated['password']
            else:
                del validated['uri']

        config.add_validator(custom_validator)

    def distribute(self, data):
        from pymongo import MongoClient

        # Allow to filter data
        super().distribute(data)

        # Get key
        if self.config.key.value is None:
            key = None

        else:
            current = data
            for part in self.config.key.value.split('.'):
                current = current[part]

            key = current

        # Determine connection parameters
        options = {
            'ssl': self.config.ssl.value,
        }

        if self.config.uri.value is not None:
            options['host'] = self.config.uri.value
        else:
            options['host'] = self.config.host.value
            options['port'] = self.config.port.value
            options['username'] = self.config.username.value
            options['password'] = self.config.password.value

        # Connect to MongoDB server
        client = MongoClient(**options)
        version = client.server_info()['version']
        log.info('Connected to MongoDB version {}'.format(version))

        # Get database
        database = client[self.config.database.value]

        # Transform data
        log.info('Converting data to be safe for MongoDB')
        data = mongodb_safe(
            data,
            self.config.dotreplace.value,
            self.config.dollarreplace.value,
        )

        # Set key if available
        document_id = {}
        if key is not None:
            log.info('Using key {} = {}'.format(self.config.key.value, key))
            document_id['_id'] = key

        # Fetch collections and data units
        collection = self.config.collection.value
        if collection is None:
            bundles = [
                (database[key], value) for key, value in data.items()
            ]
        else:
            bundles = [
                (database[collection], data)
            ]

        # Insert data
        for dbcollection, bundle in bundles:
            bundle.update(document_id)

            inserted_id = dbcollection.insert_one(bundle).inserted_id
            log.info(
                'Inserted document with id {} in {}.{}'.format(
                    inserted_id, database.name, dbcollection.name
                )
            )


__all__ = ['MongoDBSink']
