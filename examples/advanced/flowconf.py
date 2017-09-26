from pathlib import Path

from flowbber.loaders import source
from flowbber.components import Source


@source.register('my_source')
class MySource(Source):
    def collect(self):
        return {'my_value': 1000}


def get_template(template_name):
    template = Path(__file__).resolve().parent / (template_name + '.tpl')
    return template.read_text(encoding='utf-8')


def filter_coverage_class(value, threshold=(0.5, 0.8)):
    lower, higher = threshold
    if value < lower:
        return 'low'
    if value < higher:
        return 'mid'
    return 'high'
