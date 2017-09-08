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
Schema for the pipeline definition data structure.
"""

from cerberus import Validator

from .logging import get_logger


log = get_logger(__name__)


SLUG_REGEX = r'^[a-zA-Z][a-zA-Z0-9_]*$'


SLUG_SCHEMA = {
    'required': True,
    'type': 'string',
    'regex': SLUG_REGEX,
}


COMPONENT_SCHEMA = {
    'type': SLUG_SCHEMA,
    'id': SLUG_SCHEMA,
    'optional': {
        'type': 'boolean',
        'required': False,
        'default': False,
    },
    'timeout': {
        'coerce': 'timedelta_nullable',
        'required': False,
        'default': None,
        'nullable': True,
        'min': 0,
    },
    'config': {
        'required': False,
        'type': 'dict',
        'default': None,
        'nullable': True,
        'keyschema': {
            'type': 'string',
            'regex': SLUG_REGEX,
        },
    },
}


SCHEDULER_SCHEMA = {
    'frequency': {
        'required': True,
        'coerce': 'timedelta',
    },
    'samples': {
        'required': False,
        'type': 'integer',
        'min': 1,
        'nullable': True,
        'default': None,
    },
    'start': {
        'required': False,
        'type': 'integer',
        'min': 0,
        'nullable': True,
        'default': None,
    },
    'stop_on_failure': {
        'required': False,
        'type': 'boolean',
        'default': False,
    }
}


PIPELINE_SCHEMA = {
    'schedule': {
        'required': False,
        'type': 'dict',
        'schema': SCHEDULER_SCHEMA,
    },
    'sources': {
        'required': True,
        'type': 'list',
        'empty': False,
        'schema': {
            'type': 'dict',
            'schema': COMPONENT_SCHEMA,
        },
    },
    'aggregators': {
        'required': False,
        'type': 'list',
        'empty': True,
        'default': [],
        'schema': {
            'type': 'dict',
            'schema': COMPONENT_SCHEMA,
        },
    },
    'sinks': {
        'required': True,
        'type': 'list',
        'empty': False,
        'schema': {
            'type': 'dict',
            'schema': COMPONENT_SCHEMA,
        },
    },
}


class TimedeltaValidator(Validator):
    """
    Cerberus validator that allows to coerce a string to a positive integer as
    a timedelta in seconds.

    For this transformation the pytimeparse library is used.

    .. _pytimeparse: https://github.com/wroberts/pytimeparse
    """

    def _normalize_coerce_timedelta_nullable(self, value):
        if value is None:
            return None
        return self._normalize_coerce_timedelta(value)

    def _normalize_coerce_timedelta(self, value):
        from pytimeparse import parse

        if isinstance(value, int):
            return value

        timedelta = parse(value)
        if timedelta is None:
            raise ValueError('Unable to parse timedelta {}'.format(value))

        return timedelta


__all__ = ['TimedeltaValidator']
