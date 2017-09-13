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

GitHub
======

This source collects pull requests and issues statistics from a GitHub
repository using the GitHub API v3. This source requires a
`personal access token`_, you can create one in your
`settings <https://github.com/settings/tokens>`_.
No particular scope is required.

.. _personal access token: https://help.github.com/articles/creating-a-personal-access-token-for-the-command-line/


**Data collected:**

.. code-block:: json

    {
        "issue": {
            "closed": 1,
            "open": 2
        },
        "pr": {
            "closed": 3,
            "open": 4
        }
    }

**Dependencies:**

.. code-block:: sh

    pip3 install flowbber[github]

**Usage:**

.. code-block:: json

    {
        "sources": [
            {
                "type": "github",
                "id": "...",
                "config": {
                    "token": "abcdefabcdefabcdefabcdef",
                    "repository": "organization/repository",
                    "base_url": "https://api.github.com"
                }
            }
        ]
    }

token
-----

Personal access token to use to connect to the GitHub API. Keep this value safe
and secret.

- **Default**: ``N/A``
- **Optional**: ``False``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'string',
         'empty': False,
     }

- **Secret**: ``True``

repository
----------

Name of the repository to query for in the form ``organization/repository``.

- **Default**: ``N/A``
- **Optional**: ``False``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'string',
         'empty': False,
     }

- **Secret**: ``False``

base_url
--------

Base URL to connect to the GitHub v3 API.

For public GitHub, the default ``https://api.github.com`` should be used.
For private GitHub Enterprise instances use
``https://github.yourdomain.com/api/v3`` or similar.

- **Default**: ``https://api.github.com``
- **Optional**: ``True``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'string',
         'empty': False,
     }

- **Secret**: ``False``

"""  # noqa

from functools import reduce

from flowbber.components import Source


class GitHubSource(Source):

    def declare_config(self, config):
        config.add_option(
            'token',
            schema={
                'type': 'string',
                'empty': False,
            },
            secret=True,
        )

        config.add_option(
            'repository',
            schema={
                'type': 'string',
                'empty': False,
            },
        )

        config.add_option(
            'base_url',
            default='https://api.github.com',
            optional=True,
            schema={
                'type': 'string',
                'empty': False,
            },
        )

    def collect(self):
        from github import Github

        client = Github(
            login_or_token=self.config.token.value,
            base_url=self.config.base_url.value,
        )

        data = {
            'issue': {
                'closed': 0,
                'open': 0,
            },
            'pr': {
                'closed': 0,
                'open': 0,
            },
        }

        def reducer(accumulator, issue):
            accumulator[issue.state] += 1
            return accumulator

        for itype, accumulator in data.items():
            reduce(
                reducer,
                client.search_issues(
                    '', repo=self.config.repository.value, type=itype
                ),
                accumulator
            )

        return data


__all__ = ['GitHubSource']
