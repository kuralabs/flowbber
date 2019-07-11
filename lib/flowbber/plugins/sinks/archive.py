# -*- coding: utf-8 -*-
#
# Copyright (C) 2017-2019 KuraLabs S.R.L
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

Archive
=======

This sink writes all collected data to a JSON file.

.. important::

   This class inherits several inclusion and exclusion configuration options
   for filtering data before using it. See :ref:`filter-sink-options` for more
   information.

**Dependencies:**

.. code-block:: sh

    pip3 install flowbber[archive]

**Usage:**

.. code-block:: toml

    [[sinks]]
    type = "archive"
    id = "..."

        [sinks.config]
        output = "data.json"
        encoding = "utf-8"
        override = true
        create_parents = true
        pretty = false
        compress = false

.. code-block:: json

    {
        "sinks": [
            {
                "type": "archive",
                "id": "...",
                "config": {
                    "output": "data.json",
                    "encoding": "utf-8",
                    "override": true,
                    "create_parents": true,
                    "pretty": false,
                    "compress": false
                }
            }
        ]
    }

output
------

Path to JSON file to write the collected data.

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

Encoding to use to encode the file.

- **Default**: ``utf-8``
- **Optional**: ``True``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'string',
         'empty': False,
     }

- **Secret**: ``False``

override
--------

Override output file if already exists.

- **Default**: ``False``
- **Optional**: ``True``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'boolean',
     }

- **Secret**: ``False``

create_parents
--------------

Create output file parent directories if don't exist.

- **Default**: ``False``
- **Optional**: ``True``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'boolean',
     }

- **Secret**: ``False``

pretty
------

Pretty output.

- **Default**: ``False``
- **Optional**: ``True``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'boolean',
     }

- **Secret**: ``False``

compress
--------

Compress the JSON output file in a Zip archive.

If using compression, the ``.zip`` extension will be automatically appended
to the ``output`` filename parameter if not present.

The created archive will contain a JSON file named as the ``output`` parameter
without the ``.zip`` extension. For example:

======================  ====================  ====================  ================
``compress`` parameter  ``output`` parameter  Saved as              File inside Zip
======================  ====================  ====================  ================
``True``                ``archive.json``      ``archive.json.zip``  ``archive.json``
``True``                ``archive.json.zip``  ``archive.json.zip``  ``archive.json``
======================  ====================  ====================  ================

Compression uses Python's ``ZipFile`` module using the ``ZIP_DEFLATED`` option,
thus requiring the ``zlib`` module.

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
from zipfile import ZipFile, ZIP_DEFLATED

from flowbber.components import FilterSink
from flowbber.logging import get_logger


log = get_logger(__name__)


class ArchiveSink(FilterSink):
    def declare_config(self, config):
        super().declare_config(config)

        config.add_option(
            'output',
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
            'override',
            default=False,
            optional=True,
            schema={
                'type': 'boolean',
            },
        )
        config.add_option(
            'create_parents',
            default=True,
            optional=True,
            schema={
                'type': 'boolean',
            },
        )
        config.add_option(
            'pretty',
            default=False,
            optional=True,
            schema={
                'type': 'boolean',
            },
        )
        config.add_option(
            'compress',
            default=False,
            optional=True,
            schema={
                'type': 'boolean',
            },
        )

    def distribute(self, data):
        from ujson import dumps

        # Allow to filter data
        super().distribute(data)

        encoding = self.config.encoding.value
        outfile = Path(self.config.output.value)

        # Re-check no file exists, in case it was created during execution
        if outfile.is_file() and not self.config.override.value:
            raise FileExistsError(
                'File {} already exists'.format(outfile)
            )

        # Create parent directories
        if self.config.create_parents.value:
            outfile.parent.mkdir(parents=True, exist_ok=True)

        if not outfile.parent.is_dir():
            raise FileNotFoundError(
                'No such directory {}'.format(outfile.parent)
            )

        # Pretty output
        kwargs = {
            'ensure_ascii': False,
            'escape_forward_slashes': False,
        }
        if self.config.pretty.value:
            kwargs['indent'] = 4

        content = dumps(data, **kwargs)

        # Write plain file
        if not self.config.compress.value:
            log.info('Archiving data to {}'.format(outfile))
            outfile.write_text(content, encoding=encoding)
            return

        # Write compressed file
        if outfile.suffix != '.zip':
            outfile = Path(outfile.parent / '{}.zip'.format(outfile.name))

        log.info('Archiving compressed data to {}'.format(outfile))
        with outfile.open(mode='wb') as fd:
            with ZipFile(fd, mode='w', compression=ZIP_DEFLATED) as zfd:
                zfd.writestr(outfile.stem, content.encode(encoding))


__all__ = ['ArchiveSink']
