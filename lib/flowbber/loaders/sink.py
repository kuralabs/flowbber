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
Module implementating Sink base class.

All custom Flowbber sinks must extend from the Sink class.
"""

from logging import getLogger
from collections import OrderedDict

from ..entities import Sink
from .loader import PluginLoader


log = getLogger(__name__)


class SinksLoader(PluginLoader):
    """
    Sinks plugins loader class.
    """

    _base_class = Sink
    _locally_registered = OrderedDict()

    def __init__(self):
        super().__init__('sinks')


register = SinksLoader.register


__all__ = ['SinksLoader', 'register']
