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
        "pythonhashseed": 720667772
    }

**Dependencies:**

.. code-block:: sh

    pip3 install flowbber[env]

**Usage:**

Variables will be collected if the name of the variable match any item in  the
``include`` list but **DOES NOT** match any item in the ``exclude`` list.

Variables names will be stored in lowercase if the ``lowercase`` option is set
to ``true`` (the default).

Optionally, a type can be specified for each environment variable, so that it
is parsed, interpreted and collected with the expected datatype.

.. code-block:: toml

    [[sources]]
    type = "env"
    id = "..."

        [sources.config]
        include = ["PYTHONHASHSEED"]
        exclude = []
        lowercase = true

        [sources.config.types]
        PYTHONHASHSEED = "integer"

.. code-block:: json

    {
        "sources": [
            {
                "type": "env",
                "id": "...",
                "config": {
                    "include": [
                        "PYTHONHASHSEED"
                    ],
                    "exclude": [],
                    "lowercase": true,
                    "types": {
                        "PYTHONHASHSEED": "integer"
                    }
                }
            }
        ]
    }

Filtering examples:

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

*Using with Jenkins CI*

This source is very helpful to collect information from Jenkins_ CI:

.. _Jenkins: https://wiki.jenkins.io/display/JENKINS/Building+a+software+project#Buildingasoftwareproject-belowJenkinsSetEnvironmentVariables

.. code-block:: toml

    [[sources]]
    type = "env"
    id = "jenkins"

        [sources.config]
        include = [
            "BUILD_NUMBER",
            "JOB_NAME",
            "GIT_COMMIT",
            "GIT_URL",
            "GIT_BRANCH",
            "BUILD_TIMESTAMP"
        ]
        lowercase = false

        [sources.config.types]
        BUILD_NUMBER = "integer"
        BUILD_TIMESTAMP = "iso8601"

.. note::

   To parse the ``BUILD_TIMESTAMP`` variable as ISO 8601 the format needs to be
   set to ISO 8601. For more information visit:

   https://wiki.jenkins.io/display/JENKINS/Build+Timestamp+Plugin

.. code-block:: json

    {
        "sources": [
            {
                "type": "env",
                "id": "jenkins",
                "config": {
                    "include": [
                        "BUILD_NUMBER",
                        "JOB_NAME",
                        "GIT_COMMIT",
                        "GIT_URL",
                        "GIT_BRANCH",
                        "BUILD_TIMESTAMP"
                    ],
                    "lowercase": false,
                    "types": {
                        "BUILD_NUMBER": "integer"
                    }
                }
            }
        ]
    }

include
-------

List of patterns of environment variables to include.

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
             'empty': False,
         },
     }

- **Secret**: ``False``

exclude
-------

List of patterns of environment variables to exclude.

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
             'empty': False,
         },
     }

- **Secret**: ``False``

lowercase
---------

Store variables names in lowercase.

- **Default**: ``True``
- **Optional**: ``True``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'boolean',
     }

- **Secret**: ``False``

types
-----

Specify the data type of the environment variables.

At the time of this writing, the types allowed are:

:integer: Using Python's ``int()`` function.
:float: Using Python's ``float()`` function.
:string: Using Python's ``str()`` function.
:auto: Using Flowbber's :py:func:`flowbber.utils.types.autocast`.
:boolean: Using Flowbber's :py:func:`flowbber.utils.types.booleanize`.
:iso8601: Using Flowbber's :py:func:`flowbber.utils.iso8601.iso8601_to_datetime`.

- **Default**: ``None``
- **Optional**: ``True``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'dict',
         'keysrules': {
             'type': 'string',
             'empty': False,
         },
         'valuesrules': {
             'type': 'string',
             'empty': False,
             'allowed': list(TYPE_PARSERS),
         },
     }

- **Secret**: ``False``

"""  # noqa

from flowbber.components import Source
from flowbber.utils.filter import is_wanted
from flowbber.utils.types import booleanize, autocast
from flowbber.utils.iso8601 import iso8601_to_datetime


TYPE_PARSERS = {
    'integer': int,
    'float': float,
    'string': str,
    'auto': autocast,
    'boolean': booleanize,
    'iso8601': iso8601_to_datetime,
}


class EnvSource(Source):

    def declare_config(self, config):
        config.add_option(
            'include',
            default=[],
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

        config.add_option(
            'lowercase',
            default=True,
            optional=True,
            schema={
                'type': 'boolean',
            },
        )

        config.add_option(
            'types',
            default=None,
            optional=True,
            schema={
                'type': 'dict',
                'keysrules': {
                    'type': 'string',
                    'empty': False,
                },
                'valuesrules': {
                    'type': 'string',
                    'empty': False,
                    'allowed': list(TYPE_PARSERS),
                },
            },
        )

    def collect(self):
        from os import environ

        include = self.config.include.value
        exclude = self.config.exclude.value
        lowercase = self.config.lowercase.value
        types = self.config.types.value or {}

        data = {}

        for env, value in environ.items():
            if is_wanted(env, include, exclude):

                if env in types:
                    value = TYPE_PARSERS[types[env]](value)

                key = env if not lowercase else env.lower()
                data[key] = value

        return data


__all__ = ['EnvSource']
