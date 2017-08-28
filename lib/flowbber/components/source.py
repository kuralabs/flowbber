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
Module implementating the Source base class.

All custom Flowbber sources must extend from the Source class.
"""

from time import time
from abc import abstractmethod
from multiprocessing import Queue

from setproctitle import setproctitle

from .base import Component


class Source(Component):
    """
    Main base class to implement a Source.
    """

    def __init__(self, index, type_, id_, config):
        super().__init__(index, type_, id_, config)

        self.result = Queue(maxsize=1)
        self.duration = Queue(maxsize=1)

    def execute(self):
        setproctitle(str(self))

        start = time()
        entry = {}

        try:
            entry[self.id] = self.collect()
        finally:
            self.result.put(entry)
            self.duration.put(time() - start)

    @abstractmethod
    def collect(self):
        """
        Collect some arbitrary data.

        All sources subclasses must implement this abstract method.

        :return: A dictionary with the data collected by this source.
        :rtype: dict
        """
        pass


__all__ = ['Source']
