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

User
====

This source allows to collect information about the current user.

**Data collected:**

.. code-block:: json

    {
        "uid": 1000,
        "user": "kuralabs"
    }

**Dependencies:**

.. code-block:: sh

    pip3 install flowbber[user]

**Usage:**

.. code-block:: json

    {
        "sources": [
            {
                "type": "user",
                "id": "...",
                "config": {}
            }
        ]
    }

"""  # noqa

from flowbber.components import Source


class UserSource(Source):
    def collect(self):
        from os import getuid
        from getpass import getuser

        return {
            'uid': getuid(),
            'user': getuser(),
        }


__all__ = ['UserSource']
