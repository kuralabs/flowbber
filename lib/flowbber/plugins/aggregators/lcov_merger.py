# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 KuraLabs S.R.L
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

Lcov merger
===========

Merge two or more coverage tracefiles created with lcov_ into one new
tracefile.

.. _lcov: http://ltp.sourceforge.net/coverage/lcov.php

**Data produced**

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

    pip3 install flowbber[lcov_merger]

**Usage:**

.. code-block:: toml

    [[aggregators]]
    type = "lcov_merger"
    id = "..."

        [aggregators.config]
        keys = ["lcov_source_1","lcov_source_2", "..."]
        allow_missing_keys = true
        rc_overrides = ["lcov_branch_coverage=1"]
        remove = ["*hello2*"]

.. code-block:: json

    {
        "aggregators": [
            {
                "type": "lcov_merger",
                "id": "...",
                "config": {
                    "keys": ["lcov_source_1","lcov_source_2", "..."],
                    "allow_missing_keys": true,
                    "rc_overrides": ["lcov_branch_coverage=1"],
                    "remove": ["*hello2*"]
                }
            }
        ]
    }

keys
----

List of lcov sources.

- **Default**: ``N/A``
- **Optional**: ``False``
- **Schema**:

  .. code-block:: python3

        schema={
            'type': 'list',
            'empty': False,
            'schema': {
                'type': 'string',
                'empty': False,
            },
        },

- **Secret**: ``False``

allow_missing_keys
------------------

Ignore missing lcov source keys.

If ``True`` then any missing key, for example of an optional lcov source, will
not trigger an aggregator failure and the aggregator will proceed with the
remaining keys unaffected, unless no valid key remains (in which case you
should mark the aggregator as optional). If ``False`` then any missing key will
trigger an aggregator failure.

- **Default**: ``True``
- **Optional**: ``True``
- **Schema**:

  .. code-block:: python3

        schema={
            'type': 'boolean',
        },

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

from flowbber.utils.command import run
from flowbber.logging import get_logger
from flowbber.components import Aggregator
from flowbber.plugins.sources.lcov import LcovSource


log = get_logger(__name__)


class LcovMergerAggregator(Aggregator):

    def declare_config(self, config):
        config.add_option(
            'keys',
            optional=False,
            schema={
                'type': 'list',
                'empty': False,
                'schema': {
                    'type': 'string',
                    'empty': False,
                },
            },
        )

        config.add_option(
            'allow_missing_keys',
            default=True,
            optional=True,
            schema={
                'type': 'boolean',
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

    def accumulate(self, data):
        # Check for valid keys
        keys = self.config.keys.value
        available = set(keys) & set(data)
        missing = set(keys) - set(data)

        if not self.config.allow_missing_keys.value and missing:
            raise RuntimeError(
                'Lcov merger is missing keys {}'.format(
                    ', '.join(missing)
                )
            )

        # Read all sources tracefiles paths
        # Convert to something like:
        #   /path/to/file.info --tracefile /path/to/another.info
        tracefiles = '--add-tracefile {}'.format(
            ' --add-tracefile '.join(
                data[key]['tracefile']
                for key in sorted(available, key=lambda e: keys.index(e))
            )
        )

        # Read and concatenate all rc_overrides options
        # Convert to something like:
        #   --rc setting1=value1 --rc setting2=value2
        rc_overrides = ''
        if len(self.config.rc_overrides.value) > 0:
            rc_overrides = '--rc {}'.format(
                ' --rc '.join(self.config.rc_overrides.value)
            )

        # Check that lcov is installed on machine
        lcov = which('lcov')
        if lcov is None:
            raise RuntimeError('lcov executable not found.')

        # Create a tmp file to store the output tracefile
        tmp_file = NamedTemporaryFile(suffix='.info')
        tmp_file.close()

        output_file = Path(tmp_file.name)

        cmd = (
            '{lcov} '
            '{rc_overrides} '
            '{tracefiles} '
            '--output-file {output_file}'.format(
                lcov=lcov,
                rc_overrides=rc_overrides,
                tracefiles=tracefiles,
                output_file=output_file,
            )
        )
        log.info('Merging coverage tracefiles: "{}"'.format(cmd))
        status = run(cmd)

        if status.returncode != 0:
            raise RuntimeError(
                'Lcov failed adding data:\n{}'.format(status.stderr)
            )

        # Call lcov source with the output file to processing it and
        # create output data
        lcov_src = LcovSource(
            self._index, 'lcov', self._id,
            config={
                'source': str(output_file),
                'rc_overrides': self.config.rc_overrides.value,
                'remove': self.config.remove.value,
            }
        )

        data[self._id] = lcov_src.collect()


__all__ = ['LcovMergerAggregator']
