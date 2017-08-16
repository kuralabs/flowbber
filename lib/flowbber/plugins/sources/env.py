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
.. contents::
   :local:

Env
===

This source collects environment variables.

.. danger::

    This source can leak sensitive data. Please adjust ``include`` and
    ``exclude`` patterns accordingly.

    By default ``include`` and ``exclude`` patterns are empty, so no data will
    be collected. See **Usage** below for examples.

**Data collected:**

.. code-block:: json

    {
        "pythonhashseed": "720667772"
    }

**Dependencies:**

.. code-block:: sh

    pip3 install flowbber[env]

**Usage:**

Variables will be collected if the name of the variable match any item in  the
``include`` list but **DOES NOT** match any item in the ``exclude`` list.

Variables names will be stored in lowercase if the ``lowercase`` option is set
to ``true`` (the default).

.. code-block:: json

    {
        "sources": [
            {
                "type": "env",
                "key": "...",
                "config": {
                    "include": [
                        "PYTHONHASHSEED"
                    ],
                    "exclude": [],
                    "lowercase": true
                }
            }
        ]
    }

Configuration examples:

*Collect all environment variables*

.. code-block:: json

    {
        "include": ["*"],
        "exclude": []
    }

*Collect all except a few*

.. code-block:: json

    {
        "include": ["*"],
        "exclude": ["*KEY*", "*SECRET*"]
    }

*Collect only the ones specified*

.. code-block:: json

    {
        "include": ["PYTHONHASHSEED"],
        "exclude": []
    }

include
-------

List of patterns of environment variables to include.

Matching is performed using Python's fnmatch_.

.. _fnmatch: https://docs.python.org/3/library/fnmatch.html#fnmatch.fnmatch

- **Default**: ``[]``
- **Optional**: ``True``
- **Type**: ``list``
- **Secret**: ``False``

exclude
-------

List of patterns of environment variables to exclude.

Matching is performed using Python's fnmatch_.

.. _fnmatch: https://docs.python.org/3/library/fnmatch.html#fnmatch.fnmatch

- **Default**: ``[]``
- **Optional**: ``True``
- **Type**: ``list``
- **Secret**: ``False``

lowercase
---------

Store variables names in lowercase.

- **Default**: ``True``
- **Optional**: ``True``
- **Type**: ``bool``
- **Secret**: ``False``

"""  # noqa

from flowbber.entities import Source


class EnvSource(Source):

    def declare_config(self, config):
        config.add_option(
            'include',
            default=[],
            optional=True,
            type=list
        )

        config.add_option(
            'exclude',
            default=[],
            optional=True,
            type=list
        )

        config.add_option(
            'lowercase',
            default=True,
            optional=True,
            type=bool
        )

    def collect(self):
        from os import environ
        from fnmatch import fnmatch

        include = self.config.include.value
        exclude = self.config.exclude.value

        data = {}

        def is_included(value, patterns):
            return any(fnmatch(env, pattern) for pattern in patterns)

        for env, value in environ.items():
            if is_included(env, include) and not is_included(env, exclude):

                key = env if not self.config.lowercase.value else env.lower()
                data[key] = value

        return data


__all__ = ['EnvSource']