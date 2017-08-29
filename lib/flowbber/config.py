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
Module implementating the Configurator class.
"""

from re import match
from copy import deepcopy
from collections import OrderedDict, namedtuple

from pprintpp import pformat
from cerberus import Validator

from .schema import SLUG_REGEX
from .logging import get_logger


log = get_logger(__name__)


class MissingOptions(AttributeError):
    def __init__(self, keys):
        super().__init__(
            'Missing mandatory configuration options {}'.format(keys)
        )
        self.keys = keys


class UnknownOptions(AttributeError):
    def __init__(self, keys):
        super().__init__(
            'Unknown configuration options {}'.format(keys)
        )
        self.keys = keys


class Configurator:
    """
    A Component configuration options manager.
    """

    def __init__(self):
        self._declared = OrderedDict()
        self._validators = []

        self._configitem = namedtuple(
            'configitem',
            ['key', 'value', 'is_secret']
        )
        self._configtype = None

    def add_option(
            self, key,
            default=None, optional=False,
            schema=None, secret=False):
        """
        Declare an option.

        :param str key: Key of the configuration option. Must be representable
         as a public Python variable.
        :param default: Default value for this option if optional and no value
         was provided.
        :param bool optional: Is this option mandatory or optional. Default is
         mandatory.
        :param dict schema: Schema to validate the user value against.
        :param bool secret: Boolean indicating that the options is a secret and
         thus shouldn't be printed, logged, stored in plain text, etc.
        """
        if not key:
            raise ValueError('Missing configuration key')

        if not match(SLUG_REGEX, key):
            raise ValueError('Invalid key "{}". Valid keys match {}'.format(
                key, SLUG_REGEX
            ))

        if not isinstance(optional, bool):
            raise ValueError('optional must be a boolean')

        if schema is not None and not isinstance(schema, dict):
            raise ValueError('schema must be a dict')

        if not isinstance(secret, bool):
            raise ValueError('secret must be a boolean')

        self._declared[key] = {
            'default': default,
            'optional': optional,
            'schema': schema,
            'secret': secret,
        }

    def add_validator(self, validator):
        """
        Add a custom validation function.

        :param function validator: A custom validator function.
        """
        self._validators.append(validator)

    def validate(self, userconf):
        """
        Validate the given user configuration dictionary with the declared
        config handled by this configurator.

        :raise MissingOptions: if mandatory options are missing.
        :raise UnknownOptions: if non declared options are present.

        :param dict userconf: The user configuration.

        :return: A custom named tuple that maps the config keys with another
         named tuple that holds the name of the key, the value and the flag
         marking it as secret or not.
        :rtype: namedtuple
        """
        if not self._declared:
            self._configtype = namedtuple('config', [])
            return self._configtype()

        # All mandatory keys are present in user config
        mandatory = {
            key for key, info in self._declared.items()
            if not info['optional']
        }
        available = set(userconf.keys())

        if mandatory - available:
            raise MissingOptions(
                sorted(mandatory - available)
            )

        # Check for unknown configuration options
        declared = set(self._declared.keys())

        if available - declared:
            raise UnknownOptions(
                sorted(available - declared)
            )

        # Check schema of the options
        for key, info in self._declared.items():
            schema = info['schema']

            if key in userconf and schema is not None:
                validator = Validator({
                    key: schema
                })
                validated = validator.validated({
                    key: userconf[key]
                })

                if validated is None:
                    log.critical(
                        'Invalid config option {} = {}:\n{}'.format(
                            key, userconf[key],
                            pformat(validator.errors)
                        )
                    )
                    raise SyntaxError(
                        'Invalid config option {} = {}'.format(
                            key, userconf[key]
                        )
                    )

                userconf[key] = validated[key]

        # Add missing default values
        validated = deepcopy(userconf)
        validated.update({
            key: info['default']
            for key, info in self._declared.items()
            if key not in available
        })

        # Pass custom validators
        for validator in self._validators:
            validator(validated)

        # Log configuration
        def is_secret(key):
            return self._declared[key]['secret']

        log_config = []
        for key in self._declared.keys():

            # Allow custom validators to delete keys
            if key not in validated:
                continue

            if is_secret(key):
                log_config.append('{} = {}'.format(key, '*' * 20))
                continue

            log_config.append('{} = {}'.format(key, validated[key]))

        log.info('Using configuration:\n    {}'.format(
            '\n    '.join(log_config)
        ))

        # Create configuration type for this declared configuration
        self._configtype = namedtuple('config', validated.keys())

        # Create inmutable configuration object
        return self._configtype(**{
            key: self._configitem(
                key=key,
                value=value,
                is_secret=is_secret(key)
            )
            for key, value in validated.items()
        })


__all__ = ['Configurator']
