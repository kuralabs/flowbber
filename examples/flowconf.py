from flowbber.loaders import source
from flowbber.entities.source import Source


@source.register('my_source')
class MySource(Source):
    def collect(self):
        return {'my_value': 1000}
