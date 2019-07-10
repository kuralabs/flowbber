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

.. code-block:: toml

    [[sources]]
    type = "json"
    id = "..."

        [sources.config]
        file_uri = "file://{pipeline.dir}/file.json"
        encoding = "utf-8"
        ordered = true
        verify_ssl = true
        extract = true

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
                    "verify_ssl": true,
                    "extract": true
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

extract
-------

Extract the JSON file from a Zip archive.

If using extraction, the ``.zip`` extension will be automatically appended
to the ``file_uri`` filename parameter if not present.

It is expected that the file inside the archive matches the ``file_uri``
filename without the ``.zip`` extension. For example:

=====================  ==========================  ==========================  ========================
``extract`` parameter  ``file_uri`` parameter      File loaded                 Expected file inside Zip
=====================  ==========================  ==========================  ========================
``True``               ``xxx://archive.json``      ``xxx://archive.json.zip``  ``archive.json``
``True``               ``xxx://archive.json.zip``  ``xxx://archive.json.zip``  ``archive.json``
=====================  ==========================  ==========================  ========================

- **Default**: ``False``
- **Optional**: ``True``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'boolean',
     }

- **Secret**: ``False``

"""  # noqa

from pathlib import Path
from urllib import request
from collections import OrderedDict
from zipfile import ZipFile, ZIP_DEFLATED
from urllib.parse import urlparse, urlunparse
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
        config.add_option(
            'extract',
            default=False,
            optional=True,
            schema={
                'type': 'boolean',
            },
        )

    def collect(self):

        # Get config
        file_uri = self.config.file_uri.value
        encoding = self.config.encoding.value
        extract = self.config.extract.value

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

        def decode(fd, filename):
            if extract:
                with ZipFile(fd, mode='r', compression=ZIP_DEFLATED) as zfd:
                    content = zfd.read(filename)
            else:
                content = fd.read()
            return content.decode(encoding)

        # Parse URI
        parsed_uri = urlparse(file_uri)
        scheme = parsed_uri.scheme or 'file'
        filename = Path(parsed_uri.path)

        # Check if extraction is specified and extension is right
        if extract and filename.suffix != '.zip':
            filename = Path(
                filename.parent / '{}.zip'.format(filename.name)
            )
            file_uri = urlunparse(parsed_uri._replace(
                path='{}.zip'.format(parsed_uri.path),
            ))

        # Get source file from the file system
        if scheme == 'file':
            with filename.open(mode='rb') as fd:
                return loads(decode(fd, filename.stem))

        # Get file from an HTTP URL
        elif scheme in ['http', 'https']:

            # Disable SSL verification if requested
            context = create_default_context()
            if not self.config.verify_ssl.value:
                context.check_hostname = False
                context.verify_mode = CERT_NONE

            with request.urlopen(file_uri, context=context) as fd:
                return loads(decode(fd, filename.stem))

        raise ValueError('Unsupported scheme {}'.format(scheme))


__all__ = ['JSONSource']
