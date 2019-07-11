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
Module implementating the Sink and FilterSink base classes.

All custom Flowbber sinks must extend from the Sink class.

.. _filter-sink-options:

FilterSink Options
==================

Any Sink that inherits from the FilterSink class will have available the
following configuration options:

include
-------

List of patterns of data to include.

Matching is performed using Python's fnmatch_.

.. _fnmatch: https://docs.python.org/3/library/fnmatch.html#fnmatch.fnmatch

- **Default**: ``['*']``
- **Optional**: ``True``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'list',
         'schema': {
             'type': 'string',
         },
     }

- **Secret**: ``False``

include_files
-------------

List of paths to files containing patterns of data to include.

Matching is performed using Python's fnmatch_.

.. _fnmatch: https://docs.python.org/3/library/fnmatch.html#fnmatch.fnmatch

All unique patterns parsed from these files will be added to the ones defined
in the ``include`` configuration option.

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

List of patterns of data to exclude.

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
         },
     }

- **Secret**: ``False``

exclude_files
-------------

List of paths to files containing patterns of data to exclude.

Matching is performed using Python's fnmatch_.

.. _fnmatch: https://docs.python.org/3/library/fnmatch.html#fnmatch.fnmatch

All unique patterns parsed from these files will be added to the ones defined
in the ``exclude`` configuration option.

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

"""

from abc import abstractmethod

from .base import Component
from ..utils.filter import filter_dict, load_filter_file


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
    Common sink base class that adds several inclusion and exclusion
    configuration options for filtering data before using it.

    See :ref:`filter-sink-options` for more information.
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
            'include_files',
            default=[],
            optional=True,
            schema={
                'type': 'list',
                'schema': {
                    'type': 'string',
                    'empty': False,
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
            'exclude_files',
            default=[],
            optional=True,
            schema={
                'type': 'list',
                'schema': {
                    'type': 'string',
                    'empty': False,
                },
            },
        )

    @abstractmethod
    def distribute(self, data):
        include = self.config.include.value
        for include_file in self.config.include_files.value:
            for pattern in load_filter_file(include_file):
                if pattern not in include:
                    include.append(pattern)

        exclude = self.config.exclude.value
        for exclude_file in self.config.exclude_files.value:
            for pattern in load_filter_file(exclude_file):
                if pattern not in exclude:
                    exclude.append(pattern)

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
