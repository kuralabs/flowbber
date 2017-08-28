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

CPU
===

This source collects information about the system's CPUs load.

**Data collected:**

.. code-block:: json

    {
        "num_cpus": 2,
        "system_load": 25.0,
        "per_cpu": [40.0, 10.0]
    }

**Dependencies:**

.. code-block:: sh

    pip3 install flowbber[cpu]

**Usage:**

.. code-block:: json

    {
        "sources": [
            {
                "type": "cpu",
                "id": "...",
                "config": {}
            }
        ]
    }

"""  # noqa

from flowbber.components import Source


class CPUSource(Source):
    def collect(self):
        from psutil import cpu_percent

        load_data = cpu_percent(interval=1, percpu=True)
        num_cpus = len(load_data)

        return {
            'num_cpus': num_cpus,
            'system_load': sum(load_data) / num_cpus,
            'per_cpu': load_data
        }


__all__ = ['CPUSource']
