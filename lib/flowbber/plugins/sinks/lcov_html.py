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

Lcov HTML
=========

This sink plugin run lcov_ ``genhtml`` executable to generate a html report of
coverage.

.. note::

   This sink requires the ``genhtml`` executable to be available in your system
   to run.

.. _lcov: http://ltp.sourceforge.net/coverage/lcov.php

**Dependencies:**

.. code-block:: sh

    pip3 install flowbber[lcov]

**Usage:**

.. code-block:: json

    {
        "sinks": [
            {
                "type": "lcov_html",
                "id": "...",
                "config": {
                    "key": "<id of lcov source>",
                    "output": "<output directory>",
                    "override": true,
                    "create_parents": true
                }
            }
        ]
    }

key
---

Id of a lcov source in the pipeline.

- **Default**: ``N/A``
- **Optional**: ``False``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'string',
         'empty': False,
     }

- **Secret**: ``False``

output
------

Path to a directory to write the generated html.

- **Default**: ``N/A``
- **Optional**: ``False``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'string',
         'empty': False,
     }

- **Secret**: ``False``

override
--------

Override output directory if already exists.

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

Create output parent directories if don't exist.

- **Default**: ``True``
- **Optional**: ``True``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'boolean',
     }

- **Secret**: ``False``

"""

from pathlib import Path

from flowbber.components import Sink
from flowbber.utils.command import run


class LcovHTMLSink(Sink):
    def declare_config(self, config):
        config.add_option(
            'key',
            schema={
                'type': 'string',
                'empty': False,
            },
        )

        config.add_option(
            'output',
            default='html',
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

    def distribute(self, data):
        outdir = Path(self.config.output.value)

        if outdir.is_dir() and not self.config.override.value:
            raise FileExistsError(
                'Directory {} already exists'.format(outdir)
            )

        # Create parent directories
        if self.config.create_parents.value:
            outdir.parent.mkdir(parents=True, exist_ok=True)

        if not outdir.parent.is_dir():
            raise FileNotFoundError(
                'No such directory {}'.format(outdir.parent)
            )

        status = run(
            'genhtml --branch-coverage --output-directory {} {}'.format(
                outdir, data[self.config.key.value]['tracefile']
            )
        )

        if status.returncode != 0:
            raise RuntimeError(
                'Failed generating html coverage report:\n{}'.format(
                    status.stderr
                )
            )


__all__ = ['LcovHTMLSink']
