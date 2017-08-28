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

This sink will render specified Jinja2_ template using the collected data as
payload.

For the following collected data:

.. code-block:: python3

    OrderedDict([
        ('timestamp', {
            'epoch': 1503280511,
            'epochf': 1503280511.560432,
            'iso8601': '2017-08-20T19:55:11',
            'strftime': '2017-08-20 19:55:11',
        }),
        ('user', {'login': 'kuralabs', 'uid': 1000}),
    ])

The following template could be used:

.. code-block:: html+jinja

    <h1>My Rendered Template</h1>

    <h2>Timestamp:</h2>

    <ul>
        <li>Epoch: {{ data.timestamp.epoch }}</li>
        <li>ISO8601: {{ data.timestamp.iso8601 }}</li>
    </ul>

    <h2>User:</h2>

    <ul>
        <li>UID: {{ data.user.uid }}</li>
        <li>Login: {{ data.user.login }}</li>
    </ul>

And rendering it with that data will result in:

.. code-block:: html

    <h1>My Rendered Template</h1>

    <h2>Timestamp:</h2>

    <ul>
        <li>Epoch: 1503280511</li>
        <li>ISO8601: 2017-08-20T19:55:11</li>
    </ul>

    <h2>User:</h2>

    <ul>
        <li>UID: 1000</li>
        <li>Login: kuralabs</li>
    </ul>

.. _Jinja2: http://jinja.pocoo.org/

**Dependencies:**

.. code-block:: sh

    pip3 install flowbber[template]

**Usage:**

.. code-block:: json

    {
        "sinks": [
            {
                "type": "template",
                "id": "...",
                "config": {
                    "template": "template1.tpl",
                    "output": "render1.html",
                    "override": true,
                    "create_parents": true
                }
            }
        ]
    }

template
--------

URI to the Jinja2_ template. If no schema is specified, ``file://`` will be
used.

Supported schemas:

- ``file://`` (the default): File system path to the template.

  ::

      file://path/to/template.tpl

- ``python://``: A Python package and function name to load the content of the
  template.

  This is particularly useful if your templates are included as
  ``package_data`` in a package with your custom plugins, or you want to load
  the template using a custom logic from your ``flowconf.py`` (in which case
  use ``python://flowconf:yourfunction``).

  Specify the package using a dotted notation and the function name separated
  by a ``:`` (colon). The function mustn't receive any arguments and must
  return the content of the template.

  ::

      python://package.subpackage:function

- **Default**: ``N/A``
- **Optional**: ``False``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'string',
         'empty': False,
     }

- **Secret**: ``False``

output
------

Output file.

This option is nullable, if ``None`` is provided (the default), the output file
name will be auto-determined using the name of the template or the function
that loaded the template and appending an ``out`` file extension.

For example:

=========================================  =====================
``template``                               ``output``
=========================================  =====================
``file://templates/the_template.tpl``      ``the_template.out``
``python://mypackage.data:load_template``  ``load_template.out``
=========================================  =====================

- **Default**: ``None``
- **Optional**: ``True``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'string',
         'empty': False,
         'nullable': True
     }

- **Secret**: ``False``

override
--------

Override output file if already exists.

- **Default**: ``False``
- **Optional**: ``True``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'boolean',
     }

- **Secret**: ``False``

create_parents
--------------

Create output file parent directories if don't exist.

- **Default**: ``True``
- **Optional**: ``True``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'boolean',
     }

- **Secret**: ``False``

"""  # noqa

from pathlib import Path
from importlib import import_module

from flowbber.components import Sink
from flowbber.logging import get_logger


log = get_logger(__name__)


class TemplateSink(Sink):
    def declare_config(self, config):
        config.add_option(
            'template',
            schema={
                'type': 'string',
                'empty': False,
            },
        )

        config.add_option(
            'output',
            default=None,
            optional=True,
            schema={
                'type': 'string',
                'empty': False,
                'nullable': True
            },
        )

        config.add_option(
            'override',
            default=False,
            optional=True,
            schema={
                'type': 'boolean',
            },
        )

        config.add_option(
            'create_parents',
            default=True,
            optional=True,
            schema={
                'type': 'boolean',
            },
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
