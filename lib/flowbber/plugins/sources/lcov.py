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

This source uses lcov to generate standard Cobertura_ XML files and then
parses its contents with the cobertura source

.. _Cobertura: http://cobertura.github.io/cobertura/


**Data collected:**

.. code-block:: json

    {
        "files": {
            "my_source_code.c": {
                "total_statements": 40,
                "total_misses": 20,
                "line_rate": 0.5
            },
            "another_source.c": {
                "total_statements": 40,
                "total_misses": 40,
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

Path to the .gcda files directory

- **Optional**: ``False``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'list',
         'empty': False
     }


- **Secret**: ``False``

rc_overrides
------------

Override lcov configuration file setting.

Elements should have the form SETTING=VALUE

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
-------

List of patterns of files to remove from coverage computation.

Patterns will be interpreted as shell wild‐card patterns


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

from lcov_cobertura import LcovCobertura

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

    def collect(self):
        # Check if file exists
        directory = Path(self.config.directory.value)
        if not directory.is_dir():
            raise FileNotFoundError(
                'No such directory {}'.format(directory)
            )
        directory = directory.resolve()

        # Create a temporary file
        tmp_file = NamedTemporaryFile()
        # Close it, we just needed the name
        tmp_file.close()
        tracefile = Path(tmp_file.name)
        result = {'tracefile': str(tracefile)}

        lcov = which('lcov')
        if lcov is None:
            raise Exception('lcov binary not found')

        rc_overrides = ''
        # Transform from list to something like
        # --rc setting1=value1 --rc setting2=value2
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
        log.info('Gathering coverage info "{}"'.format(cmd))
        status = run(cmd)

        if status.returncode != 0:
            raise RuntimeError(
                'Lcov failed capturing data {}'.format(status.stderr)
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
            log.info('Removing files "{}"'.format(cmd))
            status = run(cmd)

            if status.returncode != 0:
                raise RuntimeError(
                    'Lcov failed removing files from coverage {}'.format(
                        status.stderr
                    )
                )

        # Create cobertura xml file
        converter = LcovCobertura(tracefile.open().read())
        cobertura = converter.convert()

        xml = Path('coverage.xml')
        xml.open('w').write(cobertura)

        cobertura = CoberturaSource(
            self._index, 'cobertura', self._id, config={'xmlpath': str(xml)}
        )

        result.update(cobertura.collect())
        return result


__all__ = ['LcovSource']
