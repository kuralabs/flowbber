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
Input pipeline definition formats parses.
"""

from pprintpp import pformat
from cerberus import Validator

from .logging import get_logger
from .namespaces import get_namespaces


SLUG_REGEX = r'^[a-zA-Z_][a-zA-Z0-9_]*$'


SLUG_SCHEMA = {
    'required': True,
    'type': 'string',
    'regex': SLUG_REGEX,
}


COMPONENT_SCHEMA = {
    'type': SLUG_SCHEMA,
    'id': SLUG_SCHEMA,
    'config': {
        'required': False,
        'type': 'dict',
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


log = get_logger(__name__)


class PipelineValidator(Validator):
    """
    FIXME: Document.
    """

    def _normalize_coerce_timedelta(self, value):
        from pytimeparse import parse

        timedelta = parse(value)
        if timedelta is None:
            raise ValueError('Unable to parse timedelta {}'.format(value))

        return timedelta


def replace_values(definition, path):
    """
    FIXME: Document.
    """

    namespaces = get_namespaces(path)

    # Replace all string keys and values
    def replace(obj):
        if isinstance(obj, str):
            return obj.format(**namespaces)

        if isinstance(obj, list):
            return [replace(element) for element in obj]

        if isinstance(obj, dict):
            return {
                replace(key): replace(value)
                for key, value in obj.items()
            }

        return obj

    return replace(definition)


def load_pipeline_json(path):
    """
    FIXME: Document.
    """
    from ujson import loads
    return loads(path.read_text(encoding='utf-8'))


def load_pipeline_toml(path):
    """
    FIXME: Document.
    """
    from toml import loads
    return loads(path.read_text(encoding='utf-8'))


def load_pipeline(path):
    """
    FIXME: Document.
    """
    supported_formats = {
        '.toml': load_pipeline_toml,
        '.json': load_pipeline_json,
    }

    extension = path.suffix
    if extension not in supported_formats:
        raise RuntimeError(
            'Unknown pipeline format "{}". Supported formats are :{}.'.format(
                extension, sorted(supported_formats.keys())
            )
        )

    try:
        definition = supported_formats[extension](path)
    except Exception as e:
        log.critical('Unable to parse pipeline definition {}'.format(path))
        raise e

    # Replace string values that required replacement
    definition = replace_values(definition, path)

    # Validate data structure
    validator = PipelineValidator(PIPELINE_SCHEMA)
    validated = validator.validated(definition)

    if validated is None:
        log.critical(
            'Invalid pipeline definition:\n{}'.format(
                pformat(validator.errors)
            )
        )
        raise SyntaxError('Invalid pipeline definition')

    log.info('Pipeline definition loaded, realized and validated.')
    log.debug(pformat(validated))
    return validated


__all__ = ['load_pipeline']
