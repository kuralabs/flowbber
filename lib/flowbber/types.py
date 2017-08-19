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
Flowbber general utilities for specifying types.
"""


def nullable(type_):
    """
    Wrap a type function so that if None is passed it returns None instead of
    the converted value of None.
    """

    def nullable_type(value):
        if value is None:
            return None
        return type_(value)

    if hasattr(type_, '__name__'):
        nullable_type.__name__ = 'nullable_{}'.format(type_.__name__)

    return nullable_type


__all__ = ['nullable']
