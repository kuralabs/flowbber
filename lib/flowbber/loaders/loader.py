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
Base class to load Flowbber plugins.

All Flowbber entity loaders extend from the PluginLoader class.
"""

import logging
from copy import copy
from inspect import isclass
from collections import OrderedDict

from pkg_resources import iter_entry_points

from ..entities import BaseEntity


log = logging.getLogger(__name__)


class PluginLoader(object):
    """
    Plugin loader utility class.

    This class allows to load plugins using Python entry points.

    :param str entity: Name of the entity.
    :param class base_class: Base class to check against. Any class specified
     here must comply with the :class:`BaseEntity`.
    :param str api_version: Version of the API.
    """

    def __init__(self, entity, base_class, api_version='1.0'):
        super().__init__()

        self.entrypoint = 'flowbber_plugin_{entity}_{api_version}'.format(
            entity=entity, api_version=api_version.replace('.', '')
        )

        self.base_class = base_class
        assert issubclass(self.base_class, BaseEntity)

        self._plugins_cache = OrderedDict()

    def __call__(self, cache=True):
        return self.load_plugins(cache=cache)

    def load_plugins(self, cache=True):
        """
        List all available plugins.

        This function lists all available plugins by discovering installed
        plugins registered in the entry point. This can be costly or error
        prone if a plugin misbehave. Because of this a cache is stored after
        the first call.

        :param bool cache: If ``True`` return the cached result. If ``False``
         force reload of all plugins registered for the entry point.

        :return: An ordered dictionary associating the name of the plugin and
         the class (subclass of :class:`flowbber.entities.BaseEntity`)
         implementing it.
        :rtype: OrderedDict
        """

        # Return cached value if call is repeated
        if cache and self._plugins_cache:
            return copy(self._plugins_cache)

        # Add built-in plugin types
        available = OrderedDict()

        # Iterate over entry points
        for ep in iter_entry_points(group=self.entrypoint):

            name = ep.name

            try:
                plugin = ep.load()
            except Exception:
                log.exception(
                    'Unable to load plugin {}'.format(name)
                )
                continue

            if not isclass(plugin) or not issubclass(plugin, self.base_class):
                log.error(
                    'Ignoring plugin "{}" as it doesn\'t '
                    'match the required interface: '
                    'Plugin not a subclass of {}.'.format(
                        name, self.base_class.__name__
                    )
                )
                continue

            available[name] = plugin

        self._plugins_cache = available
        return copy(self._plugins_cache)


__all__ = ['PluginLoader']
