from pathlib import Path

from flowbber.loaders import source
from flowbber.entities.source import Source


@source.register('my_source')
class MySource(Source):
    def collect(self):
        return {'my_value': 1000}


def atemplate():
    template = Path(__file__).resolve().parent / 'template1.tpl'
    return template.read_text(encoding='utf-8')