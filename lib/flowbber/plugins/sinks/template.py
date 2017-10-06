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
        ('user', {'uid': 1000, 'user': 'kuralabs'}),
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
        <li>User: {{ data.user.user }}</li>
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
        <li>User: kuralabs</li>
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

  Or if using :ref:`substitutions`:

  ::

      file://{pipeline.dir}/template.tpl

  When using this option, the selected template is able to load sibling
  templates (in the same directory) using Jinja2_ ``import`` or ``extend``
  directives:

  .. code-block:: jinja

     {% import "common.html" as common %}

  .. code-block:: jinja

     {% extends "base.html" %}

- ``python://``: A Python package and function name to load the content of the
  template.

  ::

      python://package.subpackage.function:template

  This is particularly useful if your templates are included as
  ``package_data`` in a package with your custom plugins, or you want to load
  the template using a custom logic from your ``flowconf.py``.

  Specify the package and function using a dotted notation and the template
  name separated by a ``:`` (colon). The function receives the template name as
  argument and must return the content of the template.

  For example, in your ``flowconf.py``:

  .. code-block:: python3

     from jinja2 import TemplateNotFound

     def my_loading_function(template_name):
        if template_name == 'greeting_template':
            return '<h1>Hello { data.user.name }!</h1>'
        raise TemplateNotFound(template_name)

  This can be used in your pipeline as:

  .. code-block: toml

     [[sinks]]
     type = "template"
     id = "template1"

         [sinks.config]
         template = "python://flowconf.my_loading_function:greeting_template"
         output = "greeting.html"

  When using this option, the selected template is able to load other templates
  that the function is able to resolve using Jinja2_ ``import`` or ``extend``
  directives:

  .. code-block:: jinja

     {% import "common" as common %}

  .. code-block:: jinja

     {% extends "base" %}

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
name will be auto-determined using the name of the template and
appending an ``out`` file extension.

For example:

================================================  =====================
``template``                                      ``output``
================================================  =====================
``file://templates/the_template.tpl``             ``the_template.out``
``python://mypackage.load_template:my_template``  ``my_template.out``
================================================  =====================

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

payload
-------

Extra data to pass to the template. Data provided using this configuration
option will be available to the template under the ``payload`` variable.

Usage:

.. code-block:: toml

   [[sinks]]
   type = "template"
   id = "mytemplate"

       [sinks.config.payload]
       project_name = "Flowbber"
       project_url = "https://docs.kuralabs.io/flowbber/"

And then in your template:

.. code-block:: html+jinja

   <p>Visit our project page at
       <a href="{{ payload.project_url }}">{{ payload.project_name }}</a>
   </p>

- **Default**: ``None``
- **Optional**: ``True``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'dict',
         'nullable': True,
     }

- **Secret**: ``False``

filters
-------

Custom filters to pass to the template.

This options must map the name of the filter with the path to the function that
implements it. Any path to a Python function is valid, including using the
local ``flowconf.py`` file.

Usage:

.. code-block:: toml

   [[sinks]]
   type = "template"
   id = "mytemplate"

       [sinks.config.filters]
       coverage_class = "flowconf.filter_coverage_class"

And then in your ``flowconf.py`` (or package with custom components):

.. code-block:: python3

   def filter_coverage_class(value, threshold=(0.5, 0.8)):
       lower, higher = threshold
       if value < lower:
           return 'low'
       if value < higher:
           return 'mid'
       return 'high'

The above filter can then be used as:

.. code-block:: html+jinja

   {% for filename, filedata in data.coverage.files.items() %}
   <ul>
       <li class="{{ filedata.line_rate|coverage_class }}">
           {{ filename }}
       </li>
   </ul>
   {% endfor %}

- **Default**: ``None``
- **Optional**: ``True``
- **Schema**:

  .. code-block:: python3

     {
         'type': 'dict',
         'keyschema': {
             'type': 'string',
             'empty': False,
         },
         'valueschema': {
             'type': 'string',
             'empty': False,
         },
         'nullable': True,
     }

- **Secret**: ``False``

"""  # noqa

from pathlib import Path
from importlib import import_module

from flowbber.logging import get_logger
from flowbber.components import FilterSink


log = get_logger(__name__)


def import_function(function_path):
    """
    Import and return a function specified by the given path.

    :param str function_path: Path (module, submodule) to a function, as when
     importing it in Python. For example ``module.submodule.function`` for the
     equivalent of ``from module.submodule import function``.

    :return: The function at the given path.
    :rtype: function
    """
    module_path, function_name = function_path.rsplit('.', 1)
    module = import_module(module_path)
    function = getattr(module, function_name, None)

    if function is None:
        raise ValueError('No such function {}'.format(function_path))

    return function


class TemplateSink(FilterSink):
    def declare_config(self, config):
        super().declare_config(config)

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

        config.add_option(
            'payload',
            default=None,
            optional=True,
            schema={
                'type': 'dict',
                'nullable': True,
            },
        )

        config.add_option(
            'filters',
            default=None,
            optional=True,
            schema={
                'type': 'dict',
                'keyschema': {
                    'type': 'string',
                    'empty': False,
                },
                'valueschema': {
                    'type': 'string',
                    'empty': False,
                },
                'nullable': True,
            },
        )

    def _load_filters(self):
        """
        Load filter functions from the configuration option.
        """
        filters = self.config.filters.value
        if filters is None:
            return {}

        return {
            key: import_function(function_path)
            for key, function_path in filters.items()
        }

    def distribute(self, data):
        from jinja2 import Environment, FileSystemLoader, FunctionLoader

        # Allow to filter data
        super().distribute(data)

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

            loader = FileSystemLoader(str(template_file.parent))
            template_name = template_file.name
            template_base = template_file.stem

        # Get template from Python package
        elif schema == 'python':

            function_path, template_name = template_uri.rsplit(':', 1)
            function = import_function(function_path)

            if function is None:
                raise ValueError('No such function {}'.format(function_path))

            loader = FunctionLoader(function)
            template_base = function.__name__

        else:
            raise ValueError('Unsupported schema {}'.format(schema))

        # Check output file
        outfile_path = self.config.output.value
        if outfile_path is None:
            outfile_path = '{}.out'.format(template_base)

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

        # Fetch filters
        filters = self._load_filters()

        # Create environment
        env = Environment(loader=loader)
        env.filters.update(filters)

        template = env.get_template(template_name)

        # Render template and write it
        log.info('Rendering template to {}'.format(outfile))
        rendered = template.render(
            data=data, payload=self.config.payload.value
        )
        outfile.write_text(rendered, encoding='utf-8')


__all__ = ['TemplateSink']
