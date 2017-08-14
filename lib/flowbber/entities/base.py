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
Base class for all Flowbber entities.

All Flowbber entities extend from the BaseEntity class.
"""

from abc import ABCMeta, abstractmethod

from ..config import Configurator


class NamedABCMeta(ABCMeta):
    """
    FIXME: Document.
    """

    def __str__(cls):
        return cls.__name__

    def __repr__(cls):
        return str(cls)


class BaseEntity(metaclass=NamedABCMeta):
    """
    FIXME: Document.
    """

    @abstractmethod
    def __init__(self, type_, config):
        self._type_ = type_

        configurator = Configurator()
        self.declare_config(configurator)
        self.config = configurator.validate(config)

    def declare_config(self, config):
        pass

    def __str__(self):
        return '{}.{}'.format(
            self.__class__.__name__,
            self._type_
        )

    def __repr__(self):
        return str(self)


__all__ = ['BaseEntity']
