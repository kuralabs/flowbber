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

Git
===

This source collects information from a (this) local git repository:

- The repository root path.
- The current branch.
- The current revision hash.
- The (a) tag pointing to the current revision.
- Name of the author of the current revision.
- Email of the author of the current revision.
- Commit message subject of current revision.
- Commit message body of current revision.
- Commit date in strict ISO 8601 format.

The ``directory`` option can be used to specify a path to a local git
repository to get information from. In particular, if your CI system created
an out-of-repository build directory you can always get the context of the
repository the pipeline definition file is commited to using:

.. code-block:: json

    {
        "type": "git",
        "id": "...",
        "config": {
            "directory": "{git.root}"
        }
    }


**Data collected:**

.. code-block:: json

    {
        "root": "/home/kuralabs/flowbber",
        "branch": "master",
        "rev": "9742e30",
        "tag": "2.0.0",
        "name": "The Author",
        "email": "author@domain.com",
        "subject": "Added a new Git source.",
        "body": "",
        "date": "2017-09-13T01:27:55-06:00"
    }

**Dependencies:**

.. code-block:: sh

    pip3 install flowbber[git]

**Usage:**

.. code-block:: json

    {
        "sources": [
            {
                "type": "git",
                "id": "...",
                "config": {
                    "directory": "."
                }
            }
        ]
    }

directory
---------

Directory to run git from. This can be any subdirectory inside a git
repository, not only the root.

- **Default**: ``'.'``
- **Optional**: ``True``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'string',
         'empty': False,
     }

- **Secret**: ``False``

"""  # noqa

from flowbber.components import Source
from flowbber.utils.git import (
    find_tag, find_root, find_branch, find_revision,
    find_name, find_email, find_subject, find_body, find_date,
    GitError,
)


class GitSource(Source):

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

    def collect(self):
        directory = self.config.directory.value

        # Tag lookup is the only one allowed to fail
        def get_tag():
            try:
                return find_tag(directory=directory)
            except GitError as e:
                return ''

        data = {
            'root': find_root(directory=directory),
            'branch': find_branch(directory=directory),
            'rev': find_revision(directory=directory),
            'tag': get_tag(),
            'name': find_name(directory=directory),
            'email': find_email(directory=directory),
            'subject': find_subject(directory=directory),
            'body': find_body(directory=directory),
            'date': find_date(directory=directory),
        }

        return data


__all__ = ['GitSource']
