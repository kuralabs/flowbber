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

Print
=====

This sink plugin will pretty print all collected data to ``stdout``.

This module uses third party module pprintpp_ for better pretty printing of
large data structures.

.. _pprintpp: https://github.com/wolever/pprintpp

**Dependencies:**

.. code-block:: sh

    pip3 install flowbber[print]

**Usage:**

.. code-block:: json

    {
        "sinks": [
            {
                "type": "print",
                "id": "...",
                "config": {}
            }
        ]
    }

"""

from flowbber.logging import print
from flowbber.components import FilterSink


class PrintSink(FilterSink):
    def declare_config(self, config):
        super().declare_config(config)

    def distribute(self, data):
        from pprintpp import pformat

        # Allow to filter data
        super().distribute(data)

        print(pformat(data))


__all__ = ['PrintSink']
