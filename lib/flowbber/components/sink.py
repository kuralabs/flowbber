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

from abc import abstractmethod

from .base import Component
from ..utils.filter import filter_dict


class Sink(Component):
    """
    Main base class to implement a Sink.
    """

    def __init__(
        self, index, type_, id_,
        optional=False, timeout=None, config=None
    ):
        super().__init__(
            index, type_, id_,
            optional=optional, timeout=timeout, config=config
        )

    def _component_execute(self, data):
        """
        Sink component execute override.

        This function will just call the user provided ``distribute()``
        function with the input data and return an empty dictionary
        ("no data").
        """
        self.distribute(data)
        return {}

    @abstractmethod
    def distribute(self, data):
        """
        Distribute the collected data.

        All sinks subclasses must implement this abstract method.

        :param OrderedDict data: The collected data. This dictionary can be
         modified as required without consequences for the pipeline.
        """
        pass


class FilterSink(Sink):
    """
    Common sink base class that adds a include and exclude configuration
    options and filters the data before using it.
    """

    def declare_config(self, config):
        config.add_option(
            'include',
            default=['*'],
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

    @abstractmethod
    def distribute(self, data):
        include = self.config.include.value
        exclude = self.config.exclude.value

        # Optimization when no filter is requested to the input data
        if include == ['*'] and not exclude:
            return

        filtered = filter_dict(data, include, exclude)
        data.clear()
        data.update(filtered)


__all__ = [
    'Sink',
    'FilterSink',
]
