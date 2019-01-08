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
flowbber.plugins.sources.valgrind module entry point.
"""

from pathlib import Path

from flowbber.components import Source


class ValgrindBaseSource(Source):

    def declare_config(self, config):
        config.add_option(
            'xmlpath',
            schema={
                'type': 'string',
                'empty': False,
            },
        )

    def collect(self):
        from xmltodict import parse

        # Check if file exists
        infile = Path(self.config.xmlpath.value)
        if not infile.is_file():
            raise FileNotFoundError(
                'No such file {}'.format(infile)
            )

        doc = parse(infile.read_text(), force_list=('error', 'stack',))
        return doc['valgrindoutput']


__all__ = ['ValgrindBaseSource']
