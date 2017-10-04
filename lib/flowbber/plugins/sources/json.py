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

JSON
====

This source fetch and parses a local or remote (http, https) json file.

.. _pytest: https://docs.pytest.org/


**Data collected:**

*Same as the source file*

**Dependencies:**

.. code-block:: sh

    pip3 install flowbber[json]

**Usage:**

.. code-block:: json

    {
        "sources": [
            {
                "type": "json",
                "id": "...",
                "config": {
                    "file_uri": "file://{pipeline.dir}/file.json",
                    "encoding": "utf-8",
                    "ordered": true,
                    "verify_ssl": true
                }
            }
        ]
    }

file_uri
--------

URI to the JSON file. If no schema is specified, ``file://`` will be
used.

Supported schemas:

- ``file://`` (the default): File system path to the JSON file.

  ::

      file://path/to/file.json

  Or if using :ref:`substitutions`:

  ::

      file://{pipeline.dir}/file.json

- ``http[s]://``: URL to download the JSON file.

  ::

      https://mydomain.com/archive/file.json

- **Default**: ``N/A``
- **Optional**: ``False``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'string',
         'empty': False,
     }

- **Secret**: ``False``

encoding
--------

Encoding to use to decode the file.

- **Default**: ``utf-8``
- **Optional**: ``True``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'string',
         'empty': False,
     }

- **Secret**: ``False``

ordered
-------

Parses the file in order and returns it as a `py:class:collections.OrderedDict`
instead of an unordered dictionary.

- **Default**: ``False``
- **Optional**: ``True``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'boolean'
     }

- **Secret**: ``False``

verify_ssl
----------

Enable or disable SSL verification. This option only applies if the ``https``
schema is used.

- **Default**: ``True``
- **Optional**: ``True``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'boolean'
     }

- **Secret**: ``False``

"""  # noqa

from urllib import request
from collections import OrderedDict
from ssl import create_default_context, CERT_NONE

from flowbber.components import Source


class JSONSource(Source):

    def declare_config(self, config):
        config.add_option(
            'file_uri',
            schema={
                'type': 'string',
                'empty': False,
            },
        )
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
            'ordered',
            default=False,
            optional=True,
            schema={
                'type': 'boolean'
            },
        )
        config.add_option(
            'verify_ssl',
            default=True,
            optional=True,
            schema={
                'type': 'boolean'
            },
        )

    def collect(self):

        # Get config
        file_uri = self.config.file_uri.value
        encoding = self.config.encoding.value

        # Get decoding function
        ordered = self.config.ordered.value

        if ordered:
            from json import loads as srcloads

            def loads(text):
                return srcloads(text, object_pairs_hook=OrderedDict)
        else:
            from ujson import loads as srcloads

            def loads(text):
                return srcloads(text)

        # Determine schema
        if '://' in file_uri:
            schema, resource = file_uri.split('://', 1)
        else:
            schema = 'file'
            resource = file_uri

        # Get source file from the file system
        if schema == 'file':
            with open(resource, 'rb') as fd:
                return loads(
                    fd.read().decode(encoding)
                )

        # Get file from an HTTP URL
        elif schema in ['http', 'https']:

            # Disable SSL verification if requested
            context = create_default_context()
            if not self.config.verify_ssl.value:
                context.check_hostname = False
                context.verify_mode = CERT_NONE

            with request.urlopen(file_uri, context=context) as fd:
                return loads(
                    fd.read().decode(encoding)
                )

        raise ValueError('Unsupported schema {}'.format(schema))


__all__ = ['JSONSource']
