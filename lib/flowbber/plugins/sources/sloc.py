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

SLOC
====

This source count source lines of code. It scans a directory for source code
files, identify their language and count the number of code, comments and empty
lines. It is highly tunable using include and exclude patterns as explained
below. It is implemented on top of pygount_, which is very accurate, but not
the fastest. Benchmark on HUGE code bases.

.. _pygount: https://github.com/roskakori/pygount


**Data collected:**

.. code-block:: json

    {
        "sloc": {
            "html": {
                "string": 0,
                "empty": 59,
                "code": 129,
                "documentation": 7
            },
            "python": {
                "string": 362,
                "empty": 1532,
                "code": 2262,
                "documentation": 4291
            },
            "restructuredtext": {
                "string": 73,
                "empty": 619,
                "code": 1133,
                "documentation": 19
            },
        },
        "files": {
            "setup.py": "python",
            "lib/flowbber/main.py": "python",
            "... more collected files ...": "<language detected>"
        }
    }

**Dependencies:**

.. code-block:: sh

    pip3 install flowbber[sloc]

**Usage:**

.. code-block:: json

    {
        "sources": [
            {
                "type": "sloc",
                "id": "...",
                "config": {
                    "directory": "{git.root}",
                    "include": ["*"],
                    "exclude": []
                }
            }
        ]
    }

directory
---------

Root directory to search for files.

- **Default**: ``'.'``
- **Optional**: ``True``
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

- **Default**:

  .. code-block:: python3

     [
         '.tox', '.git', '.cache',
         '__pycache__', '**/__pycache__',
         '*.pyc', '*.egg-info'
     ]

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

from os import walk
from pathlib import Path
from functools import reduce
from collections import defaultdict, OrderedDict

from flowbber.components import Source
from flowbber.logging import get_logger


log = get_logger(__name__)


def is_included(value, patterns):
    from fnmatch import fnmatch
    return any(fnmatch(value, pattern) for pattern in patterns)


def joiner(parent, collection):
    for element in collection:
        yield element, str(Path(parent, element))


def collect_files(directory, include, exclude):
    """
    Collect files from directory applying given include and exclude patterns.

    :param str directory: Directory to search for files.
    :param list include: List of include patterns.
    :param list exclude: List of exclude patterns.

    :return: List of collected relative filenames from directory.
    :rtype: list
    """
    files_collected = []

    for root, directories, files in walk(directory):
        relative = Path(root).relative_to(directory)

        directories[:] = [
            subdir
            for subdir, relsubdir in joiner(relative, directories)
            if (
                is_included(relsubdir, include) and not
                is_included(relsubdir, exclude)
            )
        ]

        files_collected.extend(
            relfname
            for _, relfname in joiner(relative, files)
            if (
                is_included(relfname, include) and not
                is_included(relfname, exclude)
            )
        )

    files_collected.sort()
    return files_collected


class SLOCSource(Source):

    def declare_config(self, config):

        config.add_option(
            'directory',
            default='.',
            optional=True,
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
            default=[
                '.tox', '.git', '.cache',
                '__pycache__', '**/__pycache__',
                '*.pyc', '*.egg-info',
            ],
            optional=True,
            schema={
                'type': 'list',
                'schema': {
                    'type': 'string',
                },
            },
        )

    def collect(self):
        from pygount import source_analysis

        directory = self.config.directory.value
        include = self.config.include.value
        exclude = self.config.exclude.value

        # Collect files
        collected = collect_files(directory, include, exclude)
        files = OrderedDict()

        # Analyze files
        def reducer(accumulator, element):

            # Perform analysis
            relfname, absfname = element

            analysis = source_analysis(
                absfname, 'flowbber', fallback_encoding='utf-8'
            )

            # Get language and register the file as analyzed
            lang = analysis.language.lower()
            files[relfname] = lang

            # Ignore unknown and binary files
            if lang in ['__unknown__', '__binary__']:
                return accumulator

            # Grab counter and perform accumulation
            counter = accumulator[lang]

            for count in ['code', 'documentation', 'empty', 'string']:
                counter[count] += getattr(analysis, count)

            return accumulator

        accumulator = defaultdict(lambda: defaultdict(lambda: 0))
        reduce(reducer, joiner(directory, collected), accumulator)

        data = {
            'files': files,
            'sloc': {
                # We transform the defaultdict to a dict
                # Defaultdicts break multiprocessing queues
                lang: dict(counter)
                for lang, counter in accumulator.items()
            },
        }
        return data


__all__ = ['SLOCSource']
