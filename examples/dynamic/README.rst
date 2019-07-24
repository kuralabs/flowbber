Run me with::

    $ flowbber --values-file values.yaml pipeline.toml.tpl

To override values in the values files (as more than one is allowed):

    $ flowbber --values-file values.yaml --values sinks.archives=2 pipeline.toml.tpl
