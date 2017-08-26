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
Base class for all Flowbber components.

All Flowbber components extend from the Component class.
"""

from abc import ABCMeta, abstractmethod

from ..config import Configurator


class NamedABCMeta(ABCMeta):
    """
    FIXME: Document.
    """

    def __str__(cls):  # noqa: False N805
        return cls.__name__

    def __repr__(cls):  # noqa: False N805
        return str(cls)


class Component(metaclass=NamedABCMeta):
    """
    FIXME: Document.
    """

    @abstractmethod
    def __init__(self, index, type_, id_, config):
        self._index = index
        self._type_ = type_
        self._id = id_

        configurator = Configurator()
        self.declare_config(configurator)
        self.config = configurator.validate(config)

    @property
    def id(self):
        return self._id

    def declare_config(self, config):
        pass

    def __str__(self):
        return '#{} {}.{}.{}'.format(
            self._index,
            self.__class__.__name__,
            self._type_,
            self._id
        )

    def __repr__(self):
        return str(self)


__all__ = ['Component']