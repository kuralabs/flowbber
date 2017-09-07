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
.. _lcov_cobertura: https://pypi.python.org/pypi/lcov_cobertura/

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
                    "xmlpath": "coverage.xml"
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

"""  # noqa

from pathlib import Path

from flowbber.components import Source


class CoberturaSource(Source):

    def declare_config(self, config):
        config.add_option(
            'xmlpath',
            schema={
                'type': 'string',
                'empty': False,
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

        cobertura = Cobertura(str(infile))

        files = {
            filename: {
                'total_statements': cobertura.total_statements(filename),
                'total_misses': cobertura.total_misses(filename),
                'line_rate': cobertura.line_rate(filename),
            }
            for filename in cobertura.files()
        }

        total = {
            'total_statements': cobertura.total_statements(),
            'total_misses': cobertura.total_misses(),
            'line_rate': cobertura.line_rate(),
        }

        return {
            'files': files,
            'total': total,
        }


__all__ = ['CoberturaSource']
