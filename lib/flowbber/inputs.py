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

from os import environ
from collections import namedtuple

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


def replace_values(definition, path):
    """
    FIXME: Document.
    """

    # Get the environment object
    safe_env = {
        key: value
        for key, value in environ.items()
        if not key.startswith('_')
    }

    env_type = namedtuple(
        'env',
        safe_env.keys()
    )
    env = env_type(**safe_env)

    # Get pipeline object
    pipeline_type = namedtuple(
        'pipeline',
        ['dir', 'ext', 'file', 'name']
    )
    pipeline = pipeline_type(
        dir=str(path.parent),
        ext=path.suffix,
        file=path.name,
        name=path.stem,
    )

    # Replace all string keys and values
    def replace(obj):
        if isinstance(obj, str):
            return obj.format(
                env=env,
                pipeline=pipeline
            )

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

    log.info('Pipeline definition loaded, realized and validated.')
    return definition


__all__ = ['load_pipeline']
