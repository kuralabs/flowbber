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

Lcov
====

This source calls lcov_ on a specified directory and process its result file
with lcov_cobertura_ to create a standard Cobertura_ XML file, which in turn
is then parsed using the flowbber Cobertura source.

.. note::

   This source requires the ``lcov`` executable to be available in your system
   to run.

.. _lcov: http://ltp.sourceforge.net/coverage/lcov.php
.. _lcov_cobertura: https://github.com/eriwen/lcov-to-cobertura-xml
.. _Cobertura: http://cobertura.github.io/cobertura/


**Data collected:**

.. code-block:: json

    {
        "files": {
            "my_source_code.c": {
                "total_statements": 40,
                "total_misses": 20,
                "branch_rate": 0.5,
                "total_hits": 8,
                "line_rate": 0.5
            },
            "another_source.c": {
                "total_statements": 40,
                "total_misses": 40,
                "branch_rate": 0.5,
                "total_hits": 8,
                "line_rate": 0.0
            }
        },
        "total": {
            "total_statements": 80,
            "total_misses": 20,
            "line_rate": 0.75
        },
        "tracefile": "<path-to-tracefile.info>"
    }

**Dependencies:**

.. code-block:: sh

    pip3 install flowbber[lcov]

**Usage:**

.. code-block:: json

    {
        "sources": [
            {
                "type": "lcov",
                "id": "...",
                "config": {
                    "directory": "{pipeline.dir}"
                    "rc_overrides": ["lcov_branch_coverage=1"]
                    "remove": ["*hello2*"]
                }
            }
        ]
    }

directory
---------

Path to the directory containing gcov's ``.gcda`` files .

- **Default**: ``N/A``
- **Optional**: ``False``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'string',
         'empty': False
     }

- **Secret**: ``False``

rc_overrides
------------

Override lcov configuration file settings.

Elements should have the form ``SETTING=VALUE``.

- **Default**: ``[]``
- **Optional**: ``False``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'list',
         'schema': {
             'type': 'string',
             'empty': False
         },
     }

- **Secret**: ``False``

remove
------

List of patterns of files to remove from coverage computation.

Patterns will be interpreted as shell wild‐card patterns.

- **Default**: ``[]``
- **Optional**: ``True``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'list',
         'schema': {
             'type': 'string',
             'empty': False,
         },
     }

- **Secret**: ``False``

"""

from shutil import which
from pathlib import Path
from tempfile import NamedTemporaryFile

from flowbber.components import Source
from flowbber.utils.command import run
from flowbber.logging import get_logger
from flowbber.plugins.sources.cobertura import CoberturaSource


log = get_logger(__name__)


class LcovSource(Source):

    def declare_config(self, config):
        config.add_option(
            'directory',
            schema={
                'type': 'string',
                'empty': False,
            },
        )

        config.add_option(
            'rc_overrides',
            default=[],
            optional=True,
            schema={
                'type': 'list',
                'schema': {
                    'type': 'string',
                    'empty': False,
                },
            },
        )

        config.add_option(
            'remove',
            default=[],
            optional=True,
            schema={
                'type': 'list',
                'schema': {
                    'type': 'string',
                    'empty': False,
                },
            },
        )

    def collect(self):
        from lcov_cobertura import LcovCobertura

        # Check if file exists
        directory = Path(self.config.directory.value)
        if not directory.is_dir():
            raise FileNotFoundError(
                'No such directory {}'.format(directory)
            )
        directory = directory.resolve()

        # Check if lcov is available
        lcov = which('lcov')
        if lcov is None:
            raise FileNotFoundError('lcov executable not found.')

        # Create a temporary file. Close it, we just need the name.
        tmp_file = NamedTemporaryFile()
        tmp_file.close()

        tracefile = Path(tmp_file.name)
        result = {
            'tracefile': str(tracefile)
        }

        # Transform from list to something like
        #   --rc setting1=value1 --rc setting2=value2
        rc_overrides = ''
        if self.config.rc_overrides.value:
            rc_overrides = '--rc {}'.format(
                ' --rc '.join(self.config.rc_overrides.value)
            )

        cmd = (
            'lcov '
            '{rc_overrides} '
            '--directory {directory} --capture '
            '--output-file {output}'.format(
                rc_overrides=rc_overrides,
                directory=directory,
                output=tracefile
            )
        )
        log.info('Gathering coverage info: "{}"'.format(cmd))
        status = run(cmd)

        if status.returncode != 0:
            raise RuntimeError(
                'Lcov failed capturing data:\n{}'.format(status.stderr)
            )

        # Remove files from patterns
        if self.config.remove.value:
            cmd = (
                'lcov '
                '{rc_overrides} '
                '--remove {tracefile} {remove} '
                '--output-file {tracefile}'.format(
                    rc_overrides=rc_overrides,
                    tracefile=tracefile,
                    remove=' '.join(
                        '"{}"'.format(e) for e in self.config.remove.value
                    )
                )
            )
            log.info('Removing files: "{}"'.format(cmd))
            status = run(cmd)

            if status.returncode != 0:
                raise RuntimeError(
                    'Lcov failed removing files from coverage:\n{}'.format(
                        status.stderr
                    )
                )

        # Create cobertura xml file and parse it
        converter = LcovCobertura(tracefile.open().read())
        cobertura_xml = converter.convert()

        with NamedTemporaryFile(delete=False) as xml:
            xml.write(cobertura_xml.encode('utf-8'))

        source = CoberturaSource(
            self._index, 'cobertura', self._id,
            config={
                'xmlpath': str(xml.name)
            }
        )

        result.update(source.collect())

        return result


__all__ = ['LcovSource']
