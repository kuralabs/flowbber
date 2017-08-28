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
Module implementating the Sink base class.

All custom Flowbber sinks must extend from the Sink class.
"""

from time import time
from abc import abstractmethod
from multiprocessing import Queue

from setproctitle import setproctitle

from .base import Component


class Sink(Component):
    """
    Main base class to implement a Sink.
    """

    def __init__(self, index, type_, id_, config):
        super().__init__(index, type_, id_, config)

        self.duration = Queue(maxsize=1)

    def execute(self, data):
        setproctitle(str(self))

        start = time()

        try:
            self.distribute(data)
        finally:
            self.duration.put(time() - start)

    @abstractmethod
    def distribute(self, data):
        """
        Distribute the collected data.

        All sinks subclasses must implement this abstract method.

        :param OrderedDict data: The collected data. This dictionary can be
         modified as required without consequences for the pipeline.
        """
        pass


__all__ = ['Sink']
