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

from abc import abstractmethod

from .base import Component


class Source(Component):
    """
    Main base class to implement a Source.
    """

    def __init__(
        self, index, type_, id_,
        optional=False, timeout=None, config=None
    ):
        super().__init__(
            index, type_, id_,
            optional=optional, timeout=timeout, config=config
        )

    def _component_execute(self):
        """
        Source component execute override.

        This function will just call the user provided ``collect()`` function,
        validate the returned value and finally return it back to the caller.
        """
        data = self.collect()

        if not isinstance(data, dict):
            raise RuntimeError(
                'Source #{source.index} "{source.id}" collected '
                'non-dictionary data'.format(
                    source=self,
                )
            )

        if not data:
            raise RuntimeError(
                'Source #{source.index} "{source.id}" didn\'t produced '
                'any data'.format(
                    source=self,
                )
            )

        return data

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
