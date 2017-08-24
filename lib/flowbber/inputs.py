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


SLUG_SCHEMA = {
    'required': True,
    'type': 'string',
    'regex': r'^[a-zA-Z0-9_-]+$',
}


ENTITY_SCHEMA = {
    'type': SLUG_SCHEMA,
    'id': SLUG_SCHEMA,
    'config': {
        'required': False,
        'type': 'dict',
    },
}


PIPELINE_SCHEMA = {
    'sources': {
        'required': True,
        'type': 'list',
        'empty': False,
        'schema': {
            'type': 'dict',
            'schema': ENTITY_SCHEMA,
        },
    },
    'aggregators': {
        'required': False,
        'type': 'list',
        'empty': True,
        'schema': {
            'type': 'dict',
            'schema': ENTITY_SCHEMA,
        },
    },
    'sinks': {
        'required': True,
        'type': 'list',
        'empty': False,
        'schema': {
            'type': 'dict',
            'schema': ENTITY_SCHEMA,
        },
    },
}


log = get_logger(__name__)


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

    # Validate data structure
    validator = Validator(PIPELINE_SCHEMA)
    if not validator.validate(definition):
        log.critical(
            'Invalid pipeline definition:\n{}'.format(
                pformat(validator.errors)
            )
        )
        raise SyntaxError('Invalid pipeline definition')

    # Add an empty aggregators list
    # Aggregators are the only entities that are allowed empty
    if 'aggregators' not in definition:
        definition['aggregators'] = []

    log.info('Pipeline definition loaded and validated')
    return definition


__all__ = ['load_pipeline']
