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
Module implementating Source base class.

All custom Flowbber sources must extend from the Source class.
"""

from functools import wraps
from collections import OrderedDict

from ..components import Source
from ..logging import get_logger
from .loader import PluginLoader


log = get_logger(__name__)


class SourcesLoader(PluginLoader):
    """
    Sources plugins loader class.
    """

    _base_class = Source
    _locally_registered = OrderedDict()

    def __init__(self):
        super().__init__('sources')


@wraps(SourcesLoader.register)
def register(key):
    return SourcesLoader.register(key)


__all__ = ['SourcesLoader', 'register']
