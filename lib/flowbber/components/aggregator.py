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
Module implementating the Aggregator base class.

All custom Flowbber aggregators must extend from the Aggregator class.
"""

from time import time
from abc import abstractmethod

from setproctitle import setproctitle

from .base import Component


class Aggregator(Component):
    """
    Main base class to implement an Aggregator.
    """

    def __init__(self, index, type_, id_, config):
        super().__init__(index, type_, id_, config)
        self.duration = None

    def execute(self, data):
        setproctitle(str(self))

        start = time()

        try:
            self.accumulate(data)
        finally:
            self.duration = time() - start

    @abstractmethod
    def accumulate(self, data):
        """
        Perform analysis or accumulate from the given data.

        The aggregator can:

        #. Add values:

           .. code-block:: python3

              data['some_key'] = {'value': 1000}

        #. Delete values:

           .. code-block:: python3

              del data['some_key']

        #. Modify values:

           .. code-block:: python3

              data['some_key']['value'] = 2000

        All aggregators subclasses must implement this abstract method.

        :param OrderedDict data: The data collected by the sources. Any
         modifications performed will be reflected on the final collected data.
        """
        pass


__all__ = ['Aggregator']
