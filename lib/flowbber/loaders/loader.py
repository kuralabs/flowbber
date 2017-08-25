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

All Flowbber component loaders extend from the PluginLoader class.
"""

from copy import copy
from inspect import isclass
from collections import OrderedDict

from pkg_resources import iter_entry_points

from ..logging import get_logger
from ..components.base import Component


log = get_logger(__name__)


class PluginLoader(object):
    """
    Plugin loader utility class.

    This class allows to load plugins using Python entry points.

    :param str component: Name of the component.
    :param class base_class: Base class to check against. Any class specified
     here must comply with the :class:`Component`.
    :param str api_version: Version of the API.
    """

    _base_class = None
    _locally_registered = None

    def __init__(self, component, api_version='1.0'):
        super().__init__()

        self.entrypoint = 'flowbber_plugin_{component}_{api_version}'.format(
            component=component, api_version=api_version.replace('.', '_')
        )

        assert issubclass(self.__class__._base_class, Component)

        self._plugins_cache = OrderedDict()

    def __call__(self, cache=True):
        return self.load_plugins(cache=cache)

    @classmethod
    def register(cls, key):
        """
        Register a plugin locally.

        This method is expected to be used as a decorator. It allows to
        register a plugin locally without having to create a full Python
        package to use entrypoints.

        Usage:

        ::

            from flowbber.loaders import source
            from flowbber.components.source import Source

            @source.register('my_source')
            class MySource(Source):
                def collect(self):
                    return {'my_value': 1000}

        Same apply for aggregators and sinks.
        """

        def decorator(plugin):
            if not all((
                isclass(plugin),
                issubclass(plugin, cls._base_class)
            )):
                raise ValueError(
                    'Plugin {} not a subclass of {}.'.format(
                        key, cls._base_class.__name__
                    )
                )

            cls._locally_registered[key] = plugin
            return plugin

        return decorator

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
         the class (subclass of :class:`flowbber.components.Component`)
         implementing it.
        :rtype: OrderedDict
        """

        # Return cached value if call is repeated
        if cache and self._plugins_cache:
            return copy(self._plugins_cache)

        # Add built-in plugin types
        available = OrderedDict()

        # Iterate over entry points
        log.debug('Loading entrypoint {}'.format(self.entrypoint))

        for ep in iter_entry_points(group=self.entrypoint):

            name = ep.name

            try:
                plugin = ep.load()
            except Exception:
                log.exception(
                    'Unable to load plugin {}'.format(name)
                )
                continue

            if not all((
                isclass(plugin),
                issubclass(plugin, self.__class__._base_class)
            )):
                log.error(
                    'Ignoring plugin "{}" as it doesn\'t '
                    'match the required interface: '
                    'Plugin not a subclass of {}.'.format(
                        name, self.__class__._base_class.__name__
                    )
                )
                continue

            available[name] = plugin

        # Load locally registered
        available.update(
            self.__class__._locally_registered
        )

        # Save cache and return
        self._plugins_cache = available
        return copy(self._plugins_cache)


__all__ = ['PluginLoader']
