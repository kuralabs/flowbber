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
Module implementing the load of local flowconf.py files.
"""

from sys import path

from .logging import get_logger


log = get_logger(__name__)


def load_configuration(pipeline_path):
    """
    Try to load local pipeline configuration flowconf.py from given directory.

    :param Path pipeline_path: Path to the parent directory of the pipeline to
     load local configuration from.
    """
    flowconf = pipeline_path / 'flowconf.py'

    if not flowconf.is_file():
        log.debug('No local flowconf.py found.')
        return

    path.append(str(pipeline_path.resolve()))
    import flowconf

    log.info('Pipeline\'s flowconf.py loaded successfully.')


__all__ = ['load_configuration']
