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

from .logging import get_logger


log = get_logger(__name__)


def replace_values(definition, path):
    """
    Perform string replacement on both keys and values of an arbitrarily nested
    dictionary data structure.

    The namespaces for the replacements are loaded with
    :func:`flowbber.namespaces.get_namespaces`.

    :param dict definition: the pipeline definition data structure.
    :param Path path: Path to the pipeline definition file.

    :return: The pipeline definition data structure with all string keys and
     values replaced with values in the namespace.
    :rtype: dict
    """
    from .namespaces import get_namespaces

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


def validate_definition(definition):
    """
    Validate given pipeline definition against the schema.

    :raise SyntaxError: if invalid pipeline definition.

    :param dict definition: The pipeline definition dictionary data structure.

    :return: The normalized and validated pipeline definition.
     This will include the default values of all optional attributes.
    :rtype: dict
    """
    from .schema import TimedeltaValidator, PIPELINE_SCHEMA

    validator = TimedeltaValidator(PIPELINE_SCHEMA)
    validated = validator.validated(definition)

    if validated is None:
        log.critical(
            'Invalid pipeline definition:\n{}'.format(
                pformat(validator.errors)
            )
        )
        raise SyntaxError('Invalid pipeline definition')

    return validated


def load_pipeline_json(path):
    """
    Load pipeline definition file in JSON format.

    :param Path path: Path to the JSON file.

    :return: A dictionary data structure with the pipeline definition.
    :rtype: dict
    """
    from ujson import loads
    return loads(path.read_text(encoding='utf-8'))


def load_pipeline_toml(path):
    """
    Load pipeline definition file in TOML format.

    :param Path path: Path to the TOML file.

    :return: A dictionary data structure with the pipeline definition.
    :rtype: dict
    """
    from toml import loads
    return loads(path.read_text(encoding='utf-8'))


def load_pipeline(path):
    """
    Load, replace and validate the pipeline definition file.

    - Path can be in any of the supported file formats.
    - Replacement values will be performed with the available namespaces.
    - Schema validation will be performed.

    :param Path path: Path to the pipeline definition file.

    :return: A dictionary data structure with the pipeline definition.
    :rtype: dict
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
    validated = validate_definition(definition)

    log.info('Pipeline definition loaded, realized and validated.')
    log.debug(pformat(validated))
    return validated


__all__ = [
    'replace_values',
    'validate_definition',
    'load_pipeline'
]
