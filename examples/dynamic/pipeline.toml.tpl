[[sources]]
type = "config"
id = "config1"

    [sources.config.data]
    home = "{env.HOME}"
    user = "{env.USER}"

    [sources.config.data.embedded]
    somefield = 123

    [sources.config.data.embedded.morefields]
    comment = "This could go forever"

{% for tsindex in range(values.sources.timestamps) -%}
[[sources]]
type = "timestamp"
id = "timestamp{{ tsindex }}"

{% endfor -%}

{%- for prindex in range(values.sinks.prints) -%}
[[sinks]]
type = "print"
id = "print{{ prindex }}"

{% endfor -%}

{%- for arindex in range(values.sinks.archives) -%}
[[sinks]]
type = "archive"
id = "print{{ prindex }}"

    [sinks.config]
    output = "archive/{{ arindex }}.json"
    override = true
    create_parents = true
    pretty = false
    compress = true

{% endfor %}
