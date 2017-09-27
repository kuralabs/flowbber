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

Cobertura
=========

This source parses standard Cobertura_ XML files.

A Cobertura file describes the coverage of source code executed by tests. This
files can be generated for several programming languages, including:

- Python, by using pytest-cov_ or coverage.py_.
- Java, by using the original Cobertura_ tool.
- C, by using GNU gcov_ to generate ``.gcno`` and ``.gcda`` coverage files,
  then processing the source tree with lcov_ to generate a ``coverage.info``
  which is finally converted to Cobertura using lcov_cobertura_.
- Go, by using gocov_ to convert a ``-coverprofile`` file and then processing
  the resulting ``coverage.json`` with gocov-xml_.

.. _pytest-cov: http://pytest-cov.readthedocs.io/
.. _coverage.py: https://coverage.readthedocs.io/

.. _Cobertura: http://cobertura.github.io/cobertura/

.. _gcov: https://gcc.gnu.org/onlinedocs/gcc/Gcov.html
.. _lcov: http://ltp.sourceforge.net/coverage/lcov.php
.. _lcov_cobertura: https://github.com/eriwen/lcov-to-cobertura-xml

.. _gocov: https://github.com/axw/gocov
.. _gocov-xml: https://github.com/AlekSi/gocov-xml


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
        }
    }

**Dependencies:**

.. code-block:: sh

    pip3 install flowbber[cobertura]

**Usage:**

.. code-block:: json

    {
        "sources": [
            {
                "type": "cobertura",
                "id": "...",
                "config": {
                    "xmlpath": "coverage.xml",
                    "include": ["*"],
                    "exclude": []
                }
            }
        ]
    }

xmlpath
-------

Path to the Cobertura ``coverage.xml`` file to be parsed.

- **Default**: ``N/A``
- **Optional**: ``False``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'string',
         'empty': False,
     }

- **Secret**: ``False``

include
-------

List of patterns of files to include.

Matching is performed using Python's fnmatch_.

.. _fnmatch: https://docs.python.org/3/library/fnmatch.html#fnmatch.fnmatch

- **Default**: ``['*']``
- **Optional**: ``True``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'list',
         'schema': {
             'type': 'string',
         },
     }

- **Secret**: ``False``

exclude
-------

List of patterns of files to exclude.

Matching is performed using Python's fnmatch_.

.. _fnmatch: https://docs.python.org/3/library/fnmatch.html#fnmatch.fnmatch

- **Default**: ``[]``
- **Optional**: ``True``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'list',
         'schema': {
             'type': 'string',
         },
     }

- **Secret**: ``False``

"""  # noqa

from pathlib import Path
from functools import reduce

from flowbber.components import Source
from flowbber.logging import get_logger
from flowbber.utils.filter import is_wanted


log = get_logger(__name__)


class CoberturaSource(Source):

    def declare_config(self, config):
        config.add_option(
            'xmlpath',
            schema={
                'type': 'string',
                'empty': False,
            },
        )

        config.add_option(
            'include',
            default=['*'],
            optional=True,
            schema={
                'type': 'list',
                'schema': {
                    'type': 'string',
                },
            },
        )

        config.add_option(
            'exclude',
            default=[],
            optional=True,
            schema={
                'type': 'list',
                'schema': {
                    'type': 'string',
                },
            },
        )

    def collect(self):
        from pycobertura import Cobertura

        # Check if file exists
        infile = Path(self.config.xmlpath.value)
        if not infile.is_file():
            raise FileNotFoundError(
                'No such file {}'.format(infile)
            )

        # Parse file
        cobertura = Cobertura(str(infile))

        # Filter files
        include = self.config.include.value
        exclude = self.config.exclude.value

        original = cobertura.files()
        relevant = [
            filename for filename in original
            if is_wanted(filename, include, exclude)
        ]

        ignored = sorted(set(original) - set(relevant))
        if ignored:
            log.info(
                '{} files ignored from total coverage'.format(len(ignored))
            )

        # Get files coverage data
        total = {
            'total_statements': 0,
            'total_misses': 0,
            'total_hits': 0,
            'branch_rate': 0.0,
            'line_rate': 0.0,
        }

        files = {
            filename: {
                key: getattr(cobertura, key)(filename=filename)
                for key in total
            }
            for filename in relevant
        }

        # Calculate total
        def reducer(accumulator, element):
            for key in ['total_statements', 'total_misses', 'total_hits']:
                accumulator[key] = accumulator.get(key, 0) + element[key]
            return accumulator

        total = reduce(reducer, files.values(), total)

        # Re-calculate total statements
        if total['total_statements']:
            total['line_rate'] = 1.0 - (
                total['total_misses'] / total['total_statements']
            )

        # Assign branch-rate
        total['branch_rate'] = cobertura.branch_rate()
        if include != ['*'] or exclude:
            log.warning(
                'Branch rate cannot be re-calculated when filtering files as '
                'the cobertura XML doesn\'t include the raw number of '
                'branches hit and total branches.'
            )

        return {
            'files': files,
            'total': total,
            'ignored': ignored,
        }


__all__ = ['CoberturaSource']
