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
Simple file archiver sink plugin.
"""

from pathlib import Path

from flowbber.entities import Sink


class ArchiveSink(Sink):
    def distribute(self):
        from ujson import dumps
        outfile = Path(self.config['output'])

        # Check if file exists
        if outfile.is_file() and not self.config.get('override', False):
            raise Exception('File {} already exists'.format(outfile))

        # Create parent directories
        if self.config.get('create_parents', True):
            outfile.parent.mkdir(parents=True, exist_ok=True)

        if not outfile.parent.is_dir():
            raise Exception('No such directory {}'.format(outfile.parent))

        outfile.write_text(dumps(self.data), encoding='utf-8')


__all__ = ['ArchiveSink']
