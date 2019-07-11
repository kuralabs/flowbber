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

Lcov
====

This source calls lcov_ on a specified directory to generate a tracefile or
loads one directly, and process it with lcov_cobertura_ to create a standard
Cobertura_ XML file, which in turn is then parsed using the flowbber Cobertura
source.

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

.. code-block:: toml

    [[sources]]
    type = "lcov"
    id = "..."

        [sources.config]
        source = "{pipeline.dir}"
        rc_overrides = ["lcov_branch_coverage=1"]
        remove = ["*hello2*"]
        remove_files = [
            "/file/with/remove/patterns",
            ".removepatterns"
        ]
        extract = ["*hello1*"]
        extract_files = [
            "/file/with/extract/patterns",
            ".extractpatterns"
        ]
        derive_func_data = false

.. code-block:: json

    {
        "sources": [
            {
                "type": "lcov",
                "id": "...",
                "config": {
                    "source": "{pipeline.dir}",
                    "rc_overrides": ["lcov_branch_coverage=1"],
                    "remove": ["*hello2*"]
                    "remove_files": [
                        "/file/with/remove/patterns",
                        ".removepatterns"
                    ],
                    "extract": ["*hello1*"],
                    "extract_files": [
                        "/file/with/extract/patterns",
                        ".extractpatterns"
                    ],
                    "derive_func_data": false,
                }
            }
        ]
    }

source
------

Path to the directory containing gcov's ``.gcda`` files or path to a tracefile
``.info`` file.

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

remove_files
------------

List of paths to files containing patterns of files to remove from coverage
computation.

Patterns will be interpreted as shell wild‐card patterns.

All unique patterns parsed from these files will be added to the ones defined
in the ``remove`` configuration option.

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

extract
-------

List of patterns of files to extract for coverage computation.

Use this option if you want to extract coverage data for only a particular
set of files from a tracefile. Patterns will be interpreted as shell wild‐card
patterns.

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

extract_files
-------------

List of paths to files containing patterns of files to extract for coverage
computation.

Patterns will be interpreted as shell wild‐card patterns.

All unique patterns parsed from these files will be added to the ones defined
in the ``extract`` configuration option.

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

derive_func_data
----------------

Allow lcov to calculate function coverage data from line coverage data.

If ``True`` then the ``--derive-func-data`` option is used on the lcov
commands. If ``False`` then the option is not used.

This option is used to collect function coverage data, even when this data is
not provided by the installed gcov tool. Instead, lcov will use line coverage
data and information about which lines belong to a function to derive function
coverage.

- **Default**: ``False``
- **Optional**: ``True``
- **Schema**:

  .. code-block:: python3

     schema={
         'type': 'boolean',
     },

- **Secret**: ``False``

"""

from shutil import which
from pathlib import Path
from tempfile import NamedTemporaryFile

from flowbber.components import Source
from flowbber.utils.command import run
from flowbber.logging import get_logger
from flowbber.utils.filter import load_filter_file
from flowbber.plugins.sources.cobertura import CoberturaSource


log = get_logger(__name__)


class LcovSource(Source):

    def declare_config(self, config):
        config.add_option(
            'source',
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

        config.add_option(
            'remove_files',
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
            'extract',
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
            'extract_files',
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
            'derive_func_data',
            default=False,
            optional=True,
            schema={
                'type': 'boolean',
            },
        )

    def collect(self):
        from lcov_cobertura import LcovCobertura

        # Check if file exists
        source = Path(self.config.source.value)
        if not source.exists():
            raise FileNotFoundError(
                'No such file or directory {}'.format(source)
            )
        source = source.resolve()

        # Check if lcov is available
        lcov = which('lcov')
        if lcov is None:
            raise FileNotFoundError('lcov executable not found.')

        # Transform from list to something like
        #   --rc setting1=value1 --rc setting2=value2
        rc_overrides = ''
        if self.config.rc_overrides.value:
            rc_overrides = '--rc {}'.format(
                ' --rc '.join(self.config.rc_overrides.value)
            )

        # Load remove patterns
        remove = self.config.remove.value
        for remove_file in self.config.remove_files.value:
            for pattern in load_filter_file(remove_file):
                if pattern not in remove:
                    remove.append(pattern)

        # Load extract patterns
        extract = self.config.extract.value
        for extract_file in self.config.extract_files.value:
            for pattern in load_filter_file(extract_file):
                if pattern not in extract:
                    extract.append(pattern)

        # Check if --derive-func-data is needed
        derive_func_data = '--derive-func-data' \
            if self.config.derive_func_data.value else ''

        if source.is_dir():
            # Create a temporary file. Close it, we just need the name.
            tmp_file = NamedTemporaryFile(suffix='.info')
            tmp_file.close()

            tracefile = Path(tmp_file.name)

            cmd = (
                '{lcov} '
                '{rc_overrides} '
                '{derive_func_data} '
                '--directory {directory} --capture '
                '--output-file {tracefile}'.format(
                    lcov=lcov,
                    rc_overrides=rc_overrides,
                    derive_func_data=derive_func_data,
                    directory=source,
                    tracefile=tracefile
                )
            )
            log.info('Gathering coverage info: "{}"'.format(cmd))
            status = run(cmd)

            if status.returncode != 0:
                raise RuntimeError(
                    'Lcov failed capturing data:\n{}'.format(status.stderr)
                )
        else:
            # Check file extension
            if source.suffix != '.info':
                raise ValueError(
                    'Unknown file extension "{}" '
                    'for a tracefile. Must be ".info"'.format(source.suffix)
                )
            tracefile = source

        result = {
            'tracefile': str(tracefile),
        }

        # Remove files from patterns
        if remove:
            cmd = (
                '{lcov} '
                '{rc_overrides} '
                '{derive_func_data} '
                '--remove {tracefile} {remove} '
                '--output-file {tracefile}'.format(
                    lcov=lcov,
                    rc_overrides=rc_overrides,
                    derive_func_data=derive_func_data,
                    tracefile=tracefile,
                    remove=' '.join(
                        '"{}"'.format(e) for e in remove
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

        # Extract files from patterns
        if extract:
            cmd = (
                '{lcov} '
                '{rc_overrides} '
                '{derive_func_data} '
                '--extract {tracefile} {extract} '
                '--output-file {tracefile}'.format(
                    lcov=lcov,
                    rc_overrides=rc_overrides,
                    derive_func_data=derive_func_data,
                    tracefile=tracefile,
                    extract=' '.join(
                        '"{}"'.format(e) for e in extract
                    )
                )
            )
            log.info('Extracting files: "{}"'.format(cmd))
            status = run(cmd)

            if status.returncode != 0:
                raise RuntimeError(
                    'Lcov failed extracting files from coverage:\n{}'.format(
                        status.stderr
                    )
                )

        # Create cobertura xml file and parse it
        converter = LcovCobertura(tracefile.open().read())
        cobertura_xml = converter.convert()

        with NamedTemporaryFile(delete=False, suffix='.xml') as xml:
            xml.write(cobertura_xml.encode('utf-8'))

        cobertura_src = CoberturaSource(
            self._index, 'cobertura', self._id,
            config={
                'xmlpath': str(xml.name)
            }
        )

        result.update(cobertura_src.collect())

        return result


__all__ = ['LcovSource']
