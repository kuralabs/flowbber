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

Template
========

Simple Jinja2 template rendering sink plugin.

FIXME: Document.
"""

from pathlib import Path
from logging import getLogger
from importlib import import_module

from flowbber.entities import Sink


log = getLogger(__name__)


class TemplateSink(Sink):
    def declare_config(self, config):
        """
        FIXME: Document.
        """
        config.add_option(
            'template',
            type=str,
        )

        config.add_option(
            'output',
            default=None,
            optional=True,
            type=str,
        )

        config.add_option(
            'override',
            default=False,
            optional=True,
            type=bool,
        )

        config.add_option(
            'create_parents',
            default=True,
            optional=True,
            type=bool,
        )

    def distribute(self, data):
        from jinja2 import Template

        # Determine schema
        template_uri = self.config.template.value

        if '://' in template_uri:
            schema, template_uri = template_uri.split('://', 1)
        else:
            schema = 'file'

        # Get template from file system
        if schema == 'file':
            template_file = Path(template_uri)
            if not template_file.is_file():
                raise FileNotFoundError(
                    'No such template {}'.format(template_uri)
                )

            template = template_file.read_text(encoding='utf-8')
            template_name = template_file.stem

        # Get template from Python package
        elif schema == 'python':

            module_path, function_name = template_uri.rsplit(':', 1)
            module = import_module(module_path)
            function = getattr(module, function_name)

            template = function()
            template_name = function_name

        else:
            raise ValueError('Unsupported schema {}'.format(schema))

        # Check output file
        outfile_path = self.config.output.value
        if outfile_path is None:
            outfile_path = '{}.out'.format(template_name)

        outfile = Path(outfile_path)

        if outfile.is_file() and not self.config.override.value:
            raise FileExistsError(
                'File {} already exists'.format(outfile)
            )

        # Create parent directories
        if self.config.create_parents.value:
            outfile.parent.mkdir(parents=True, exist_ok=True)

        if not outfile.parent.is_dir():
            raise FileNotFoundError(
                'No such directory {}'.format(outfile.parent)
            )

        # Render template and write it
        log.info('Rendering template to {}'.format(outfile))
        rendered = Template(template).render(data=data)
        outfile.write_text(rendered, encoding='utf-8')


__all__ = ['TemplateSink']
