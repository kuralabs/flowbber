# -*- coding: utf-8 -*-
#
# Copyright (C) 2017-2019 KuraLabs S.R.L
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
Utilities for filtering data.
"""

from pathlib import Path
from fnmatch import fnmatch


def included_in(value, patterns):
    """
    Check if the given value is included in the given list of patterns.

    :param str value: The value to check for.
    :param list patterns: List of patterns to check for.

    :return: True in the value is included, False otherwise.
    :rtype: bool
    """
    return any(fnmatch(value, pattern) for pattern in patterns)


def is_wanted(value, include, exclude):
    """
    Check that the given value is included in the include list and not included
    in the exclude list.

    :param str value: The value to check for.
    :param list include: List of patterns of values to include.
    :param list exclude: List of patterns of values to exclude.

    :return: True in the value is wanted, False otherwise.
    :rtype: bool
    """
    return included_in(value, include) and not included_in(value, exclude)


def filter_dict(data, include, exclude, joinchar='.'):
    """
    Filter a dictionary using the provided include and exclude patterns.

    :param dict data: The data to filter
     (dict or OrderedDict, type is respected).
    :param list include: List of patterns of key paths to include.
    :param list exclude: List of patterns of key paths to exclude.
    :param str joinchar: String used to join the keys to form the path.

    :return: The filtered dictionary.
    :rtype: dict or OrderedDict
    """
    assert isinstance(data, dict)

    def filter_dict_recursive(breadcrumbs, element):
        if not isinstance(element, dict):
            return element

        return element.__class__(
            (key, filter_dict_recursive(breadcrumbs + [key], value))
            for key, value in element.items()
            if is_wanted(joinchar.join(breadcrumbs + [key]), include, exclude)
        )

    return filter_dict_recursive([], data)


def load_filter_file(filepath, encoding='utf-8'):
    """
    Load a ".gitignore"-like file describing excluding (or including) fnmatch
    patterns.

    Empty lines and comments (#) are supported. Patterns returned are unique
    and in the same order as described in the file.

    :param str filepath: Path to the file. Path objects are also supported
     (and preferred).
    :param str encoding: Encoding to use to decode the file.

    :return: List of unique patterns in the file.
    :rtype: list
    """

    if not isinstance(filepath, Path):
        filepath = Path(filepath)

    if not filepath.exists():
        raise FileNotFoundError(
            'No such file {}'.format(filepath)
        )

    patterns = []

    with filepath.open(mode='rt', encoding=encoding) as fd:
        for raw_line in fd:
            line = raw_line.strip()

            if not line or line.startswith('#') or line in patterns:
                continue

            patterns.append(line)

    return patterns


__all__ = [
    'included_in',
    'is_wanted',
    'filter_dict',
    'load_filter_file',
]
